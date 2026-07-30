#!/usr/bin/env python3
"""
Generador de landings puente de Compara.

Produce los .html de producto a partir de un solo patrón (el validado en el piloto
Salud/CICL). Editar los datos de abajo y correr:

    python3 _docs/generate.py

Reglas que este script respeta y no hay que romper:
  - Nada inventado: los contenidos vienen del levantamiento de las LPs publicadas
    (output/_data/conteudo-lps-existentes.json en el repo Claudia) o quedan como
    placeholder TODO visible. `coberturas=None` genera el bloque con TODO.
  - El texto del CTA se repite idéntico en sus 4 apariciones.
  - Landing de compañía: hero con el logo de la aseguradora, sin fila de logos
    (mostrar competidores en una LP de marca resta foco).
  - Landing core/producto: hero con Comparini + plaquita, con fila de logos.
  - Los CTA usan [data-cotiza] y el script final conserva gclid/utm_*.
"""
import pathlib, json, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
VER = "20260729-aroldo"

FORM = {
    "salud":    "https://seguro-salud.comparaonline.cl/quote",
    "vida":     "https://seguro-vida.comparaonline.cl/quote",
    "mascotas": "https://seguro-mascotas.comparaonline.cl/quote",
}

# Plaquita del hero (aprobada por Bruno 2026-07-29: Vida C, Mascotas A, Salud A).
# Regla: la plaquita dice lo que el H1 NO dice. Si el H1 habla de precio, la plaquita
# habla de variedad, tiempo o tranquilidad. Repetir el H1 fue el error de la 1a versión.
# Largo: el titular tiene que caber en 2 líneas.
# NOTA sobre Vida: la opción C original llevaba "Desde $3.255 al mes", pero ese precio es
# de Accidentes Personales, no de Seguro de Vida (verificado en la página de producto:
# los 3 precios publicados son Vida+Ahorro $22.600, AP $3.255 y AP+Ahorro $9.925, todos
# bajo "Otros seguros que puedes contratar"). No hay precio publicado del vida temporal
# puro, así que la C va sin cifra en vez de atribuirle el precio de otro producto.
PLAQUITA = {
    "salud":    ("Compara y elige", "Todas las aseguradoras", "en un solo lugar"),
    "vida":     ("Cotiza en 5 minutos", "Protege a los tuyos", "sin letra chica"),
    "mascotas": ("Compara y elige", "El seguro de tu mascota", "sin vueltas"),
}

# Los productos de Salud llevan el dato duro del producto en la plaquita.
PLAQUITA_SLUG = {
    "salud-complementario": ("Lo que Isapre no cubre", "Consultas, exámenes y más", "compara y elige"),
    "salud-catastrofico": ("Enfermedades de alto costo", "Hasta 30.000 UF", "de tope anual"),
    "salud-ambulatorio":  ("Consultas y exámenes", "Lo que la Isapre no cubre", "compara y elige"),
    "salud-hospitalario": ("Hospitalización y cirugía", "Lo que la Isapre no cubre", "compara y elige"),
    "salud-oncologico":   ("Diagnóstico y tratamiento", "Gastos de alto costo", "compara y elige"),
    "salud-maternidad":   ("Parto y embarazo", "Lo que la Isapre no cubre", "compara y elige"),
}

HERO_IMG = {
    # Comparini. Mismo asset para los 3 BU por ahora; pedir variación para mascotas.
    "salud":    "https://res.cloudinary.com/compara/image/upload/q_auto,f_auto,c_pad,w_560,h_390/v1764182040/cms/new-uploads/img_hero_licl_pj-69274818385d53.72318176.png",
    "vida":     "https://res.cloudinary.com/compara/image/upload/q_auto,f_auto,c_pad,w_560,h_390/v1764182040/cms/new-uploads/img_hero_licl_pj-69274818385d53.72318176.png",
    "mascotas": "https://res.cloudinary.com/compara/image/upload/q_auto,f_auto,c_pad,w_560,h_390/v1764182040/cms/new-uploads/img_hero_licl_pj-69274818385d53.72318176.png",
}

# Aseguradoras por BU para la fila de logos (solo core/producto).
# Set tomado de los adgroups activos en Google Ads — pendiente de confirmación de Aroldo.
INSURERS = {
    "salud": [("logo_Consorcio.svg","Consorcio",""), ("logo_Bci.svg","BCI Seguros",""),
              ("logo_Alemana.png","Alemana Seguros",""), ("logo_CLC.svg","Clínica Las Condes",""),
              ("logo_BiceVida.svg","Bice Vida","")],
    "vida": [("logo_Consorcio.svg","Consorcio",""), ("logo_Bci.svg","BCI Seguros",""),
             ("logo_Mapfre.svg","Mapfre",""), ("logo_MetLife.png","MetLife",""),
             ("logo_Southbridge.png","Southbridge","")],
    # Mascotas: hoy solo BCI tiene adgroup activo. Con un logo la fila queda vacía y el
    # copy "las aseguradoras más importantes de Chile" no se sostiene, así que se omite.
    # Cuando entre una segunda compañía al comparador, agregarla acá y se activa sola.
    "mascotas": [],
}

PASOS = {
    "salud": [("Cuéntanos de ti", "Ingresa tus datos básicos, tu edad y tu sistema de salud actual para comenzar."),
              ("Compara precios y coberturas", "Las alternativas de las principales aseguradoras, lado a lado y sin sorpresas."),
              ("Avanza con apoyo", "Elige la opción que prefieres y recibe acompañamiento para completar el proceso.")],
    "vida": [("Cuéntanos de ti", "Tu edad, a quién quieres proteger y el capital que buscas. Toma pocos minutos."),
             ("Compara precios y coberturas", "Las alternativas de las principales aseguradoras, lado a lado y sin sorpresas."),
             ("Avanza con apoyo", "Elige la opción que prefieres y recibe acompañamiento para completar el proceso.")],
    "mascotas": [("Cuéntanos de tu mascota", "Especie, raza y edad. Con eso ya podemos mostrarte alternativas."),
                 ("Compara precios y coberturas", "Las alternativas disponibles en el mercado, lado a lado y sin sorpresas."),
                 ("Avanza con apoyo", "Elige el plan que prefieres y recibe acompañamiento para completar el proceso.")],
}

TRUST = {
    # Los de salud son los que Aroldo revisó y aprobó en la landing publicada.
    "salud":    ["Cotización online", "Opciones para ti y tu familia", "Sin compromiso"],
    "vida":     ["Todas las aseguradoras", "100% online", "Sin compromiso"],
    "mascotas": ["Todas las aseguradoras", "100% online", "Sin compromiso"],
}

ICO = {"salud":"small_icon_Seguro Salud.svg", "vida":"small_icon_Seguro Vida.svg",
       "users":"small_icon_users.svg", "headset":"small_icon_headset.svg",
       "siren":"small_icon_siren.svg", "soap":"small_icon_SOAP.svg"}

def cob(*items):
    """items: (titulo, desc, icone_key)"""
    return [{"t":t, "d":d, "i":ICO[i]} for t,d,i in items]

# ============================================================================
# LAS 21 LANDINGS
# Contenido de compañía/producto = extraído de las LP publicadas (real, no inventado).
# coberturas=None => bloque con TODO visible (falta contenido, no se inventa).
# ============================================================================
LANDINGS = [

# ---------- CORE DE PRODUCTO (3) ----------
# CONGELADA: salud.html está publicada en HubSpot y en revisión de Charlie/Aroldo
# (Bruno les pasó el link el 2026-07-28). El loader de HubSpot hace fetch de este
# archivo en vivo, así que regenerarlo cambiaría la página que están mirando.
# Se descongela cuando ellos respondan. Al descongelar, ojo con 3 diferencias que
# el generador introduce y que hay que decidir a conciencia:
#   1. Set de logos: la versión publicada tiene Zurich y Bupa; el generador pone
#      CLC y Bice Vida, que son las que SÍ tienen adgroup activo en la cuenta HICL.
#      El set del generador es el correcto por datos, pero Bruno ya mencionó el otro
#      en su mensaje de Slack.
#   2. Trust bullets publicados: "Cotización online / Opciones para ti y tu familia /
#      Sin compromiso". El generador usa "Todas las aseguradoras / 100% online /
#      Sin compromiso".
#   3. Los títulos de la sección de aseguradoras publicados llevan <span> por palabra
#      para controlar el salto de línea en mobile (hay CSS que depende: .insurers h2
#      span{display:block} en <=860px). El generador no los pone.
dict(slug="salud", bu="salud", tipo="core",
     # DESCONGELADA: Aroldo ya revisó y respondió (2026-07-29). Pasa a eje GENÉRICO porque
     # la cuenta HICL tiene adgroups genéricos ("Seguro de Salud", "Seguro Médico",
     # "Familiar", "Isapre", "Fonasa") separados de los de "Seguro Complementario", que
     # ahora tienen su propia landing (salud-complementario). Así cada grupo de búsqueda
     # tiene su match, que es lo que pidió Aroldo.
     title="Seguro de Salud | Cotiza y compara online | Compara",
     desc="Cotiza tu Seguro de Salud en 5 minutos. Compara precios y coberturas de aseguradoras reconocidas de Chile. 100% online, sin letra chica.",
     h1='Tu Seguro de Salud, al <span class="dserif">mejor</span> precio',
     sub="Compara precios y coberturas que ayudan con consultas, exámenes y hospitalizaciones. Cotiza online y elige con claridad.",
     cta="Cotiza tu Seguro de Salud",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Encuentra una opción de salud pensada para tu vida real.",
     coberturas=cob(
        ("Consultas y exámenes","Compara alternativas que ayudan con gastos médicos frecuentes.","salud"),
        ("Hospitalización y urgencias","Revisa coberturas para gastos de mayor impacto, según el plan.","siren"),
        ("Planes familiares","Alternativas pensadas para protegerte a ti y a quienes más quieres.","users"),
        ("Orientación clara","Entiende coberturas, exclusiones y próximos pasos antes de avanzar.","headset"))),

dict(slug="salud-complementario", bu="salud", tipo="core",
     # Pedida por Aroldo (2026-07-29) para dar match a los adgroups "Seguro Complementario"
     # de las campañas 1.2-B y 2.2. Mismo producto y mismas coberturas que el core de Salud:
     # lo que cambia es el eje del hero, el title y el meta, que es lo que hace el match con
     # la búsqueda. Estas landings solo reciben tráfico de Google Ads (noindex), así que dos
     # páginas del mismo producto no compiten entre sí.
     title="Seguro Complementario de Salud | Cotiza y compara online | Compara",
     desc="Cotiza tu Seguro Complementario de Salud en 5 minutos. Compara precios y coberturas de aseguradoras reconocidas de Chile. 100% online, sin letra chica.",
     h1='Tu Seguro Complementario de Salud, al <span class="dserif">mejor</span> precio',
     sub="El complemento a tu Isapre o Fonasa: compara precios y coberturas para consultas, exámenes y hospitalizaciones.",
     cta="Cotiza tu Seguro Complementario",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Complementa tu plan de salud y deja de pagar de más.",
     coberturas=cob(
        ("Consultas y exámenes","Compara alternativas que ayudan con gastos médicos frecuentes.","salud"),
        ("Hospitalización y urgencias","Revisa coberturas para gastos de mayor impacto, según el plan.","siren"),
        ("Planes familiares","Alternativas pensadas para protegerte a ti y a quienes más quieres.","users"),
        ("Orientación clara","Entiende coberturas, exclusiones y próximos pasos antes de avanzar.","headset"))),

dict(slug="vida", bu="vida", tipo="core",
     title="Seguro de Vida | Cotiza y compara online | Compara",
     desc="Cotiza tu Seguro de Vida en 5 minutos. Compara precios, capitales y coberturas de las principales aseguradoras de Chile. 100% online, sin letra chica.",
     h1='Tu Seguro de Vida, al <span class="dserif">mejor</span> precio',
     sub="Compara capitales y coberturas de las principales aseguradoras de Chile y elige cómo proteger a los tuyos. Todo online.",
     cta="Cotiza tu Seguro de Vida",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Protege a quienes más quieres, sin pagar de más.",
     coberturas=cob(
        ("Muerte por enfermedad","La cobertura base de todo Seguro de Vida del mercado.","vida"),
        ("Muerte accidental","Cobertura adicional ante fallecimiento por accidente.","siren"),
        ("Invalidez permanente","Disponible en la mayoría de los planes, según la aseguradora.","users"),
        ("Planes con ahorro","Algunas compañías acumulan parte de tu prima como ahorro.","headset"))),

dict(slug="mascotas", bu="mascotas", tipo="core",
     title="Seguro de Mascotas | Cotiza y compara online | Compara",
     desc="Cotiza el seguro de tu mascota en minutos. Compara coberturas veterinarias, reembolsos y planes disponibles en Chile. 100% online, sin letra chica.",
     h1='El seguro de tu mascota, al <span class="dserif">mejor</span> precio',
     sub="Compara coberturas veterinarias ante accidentes y enfermedades, y elige el plan que le sirve a tu perro o gato. Todo online.",
     cta="Cotiza el seguro de tu mascota",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Cuida a tu mascota sin sustos en la cuenta del veterinario.",
     coberturas=cob(
        ("Gastos veterinarios","Reembolso ante accidentes o enfermedades, según el plan.","salud"),
        ("Responsabilidad civil","Cobertura si tu mascota causa daños a terceros.","users"),
        ("Telemedicina veterinaria","Orientación remota sin salir de casa, incluida en varios planes.","headset"),
        ("Urgencias y traslado","Atención de urgencia y traslado cuando hace falta.","siren"))),

# ---------- COMPAÑÍAS DE SALUD (5) ----------
dict(slug="salud-consorcio", bu="salud", tipo="cia", marca="Consorcio",
     logo="logo_Consorcio.svg",
     title="Seguro Complementario Consorcio | Cotiza online | Compara",
     desc="Seguro Complementario Consorcio: cubre hasta el 60% de tus gastos médicos, desde 0,47 UF al mes. Cotiza online y compara con el resto del mercado.",
     h1='Seguro Complementario <span class="dserif">Consorcio</span>',
     sub="Cubre hasta el 60% de tus gastos médicos. Compara opciones desde 0,47 UF al mes.",
     cta="Cotiza tu Seguro Complementario",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda Consorcio frente al resto del mercado.",
     coberturas=cob(
        ("Tope anual de cobertura","Hasta 250 UF por beneficiario.","salud"),
        ("Red de prestadores","Libre elección.","users"),
        ("Deducible","0,5 UF por asegurado.","soap"),
        ("Inicio de vigencia","El mismo día de la contratación.","headset"),
        ("Bonificación mínima exigida","50% para Isapre y Fonasa.","siren"))),

dict(slug="salud-bci", bu="salud", tipo="cia", marca="BCI Seguros",
     logo="logo_Bci.svg",
     title="Seguro Complementario BCI Seguros | Cotiza online | Compara",
     desc="Seguro Complementario BCI Seguros: cubre hasta el 80% de tus gastos médicos, desde 0,94 UF al mes. Cotiza online y compara con el resto del mercado.",
     h1='Seguro Complementario <span class="dserif">BCI Seguros</span>',
     sub="Cubre hasta el 80% de tus gastos médicos. Compara opciones desde 0,94 UF al mes.",
     cta="Cotiza tu Seguro Complementario",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda BCI Seguros frente al resto del mercado.",
     coberturas=cob(
        ("Tope anual de cobertura","300 UF por beneficiario.","salud"),
        ("Red de prestadores","Libre elección.","users"),
        ("Deducible","0,75 UF por asegurado.","soap"),
        ("Inicio de vigencia","El mismo día de la contratación.","headset"),
        ("Bonificación mínima exigida","50% para Isapre y 35% para Fonasa.","siren"))),

dict(slug="salud-alemana", bu="salud", tipo="cia", marca="Alemana Seguros",
     logo="logo_Alemana.png",
     title="Seguro de Salud Ambulatorio Alemana | Cotiza online | Compara",
     desc="Seguro Ambulatorio Alemana: cubre tus gastos ambulatorios al 50%, sin deducible y con preexistencias incluidas. Cotiza online en Compara.",
     h1='Seguro de Salud Ambulatorio <span class="dserif">Alemana</span>',
     sub="Cubre tus gastos ambulatorios al 50%, sin deducible. Cotiza y ve tu precio en 2 minutos.",
     cta="Cotiza tu Seguro Ambulatorio",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda Alemana frente al resto del mercado.",
     coberturas=cob(
        ("Cubre preexistencias","A diferencia de la mayoría de los complementarios del mercado.","salud"),
        ("Consultas y exámenes","Diagnóstico de laboratorio e imágenes que la Isapre no reembolsa completo.","soap"),
        ("Sin deducible","No exige bonificación mínima de la Isapre.","users"),
        ("Ingreso hasta los 109 años","Con cobertura hasta los 110. Vigencia desde el primer día del mes siguiente.","headset"))),

dict(slug="salud-clc", bu="salud", tipo="cia", marca="Clínica Las Condes",
     logo="logo_CLC.svg",
     title="Seguro Catastrófico CLC | Cotiza online | Compara",
     desc="Seguro Catastrófico de Clínica Las Condes: tope anual de 30.000 UF ante enfermedades de alto costo. Cotiza online y compara en Compara.",
     h1='Seguro Catastrófico <span class="dserif">CLC</span>',
     sub="Protégete ante enfermedades de alto costo, con planes que se adaptan a ti y a tu familia.",
     cta="Cotiza tu Seguro Catastrófico",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda CLC frente al resto del mercado.",
     # OJO: la LP actual de CLC muestra contenido genérico de catastrófico (y un título
     # de Bice Vida por error). Estas coberturas son las del producto catastrófico;
     # Aroldo tiene que confirmar qué es específico de CLC.
     coberturas=cob(
        ("Tope anual de 30.000 UF","Te protege ante gastos médicos de alto costo.","salud"),
        ("Hospitalización","Cubierta ante enfermedades o accidentes catastróficos.","siren"),
        ("Exámenes de laboratorio e imagenología","Incluidos dentro de la cobertura.","soap"),
        ("Urgencia ambulatoria","Cubierta. Cobertura hasta los 110 años y 364 días.","headset"))),

dict(slug="salud-bicevida", bu="salud", tipo="cia", marca="Bice Vida",
     logo="logo_BiceVida.svg",
     title="Seguro Complementario Bice Vida | Cotiza online | Compara",
     desc="Seguro Complementario Bice Vida: hasta 50% de cobertura y tope anual de 200 UF por beneficiario. Cotiza online y compara en Compara.",
     h1='Seguro Complementario <span class="dserif">Bice Vida</span>',
     sub="Porcentaje de cobertura hasta el 50%. Cotiza y ve tu precio en 2 minutos.",
     cta="Cotiza tu Seguro Complementario",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda Bice Vida frente al resto del mercado.",
     coberturas=cob(
        ("Tope anual de cobertura","200 UF por beneficiario.","salud"),
        ("Red de prestadores","Libre elección.","users"),
        ("Deducible","0,5 UF por asegurado.","soap"),
        ("Bonificación mínima exigida","50% para Isapre y Fonasa.","siren"),
        ("Edad máxima de permanencia","Hasta los 65 años y 364 días. Vigencia el siguiente día hábil.","headset"))),

# ---------- PRODUCTOS DE SALUD (5) ----------
dict(slug="salud-catastrofico", bu="salud", tipo="producto",
     title="Seguro Catastrófico | Cotiza y compara online | Compara",
     desc="Seguro Catastrófico: tope anual de 30.000 UF ante enfermedades de alto costo. Compara las alternativas del mercado y cotiza online en Compara.",
     h1='Seguro <span class="dserif">Catastrófico</span>',
     sub="Protégete ante enfermedades de alto costo, con planes que se adaptan a ti y a tu familia.",
     cta="Cotiza tu Seguro Catastrófico",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Compara las alternativas de cobertura catastrófica y elige.",
     coberturas=cob(
        ("Tope anual de 30.000 UF","Te protege ante gastos médicos de alto costo.","salud"),
        ("Hospitalización","Cubierta ante enfermedades o accidentes catastróficos.","siren"),
        ("Exámenes de laboratorio e imagenología","Incluidos dentro de la cobertura.","soap"),
        ("Urgencia ambulatoria","Cubierta. Cobertura hasta los 110 años y 364 días.","headset"))),

dict(slug="salud-ambulatorio", bu="salud", tipo="producto",
     title="Seguro Ambulatorio | Cotiza y compara online | Compara",
     desc="Seguro Ambulatorio: cobertura para consultas médicas y exámenes que tu Isapre no reembolsa completo. Compara alternativas y cotiza online.",
     h1='Seguro <span class="dserif">Ambulatorio</span>',
     sub="Cobertura para consultas y exámenes que tu Isapre o Fonasa no reembolsa completo. Compara las alternativas del mercado.",
     cta="Cotiza tu Seguro Ambulatorio",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Compara las alternativas de cobertura ambulatoria y elige.",
     coberturas=cob(
        ("Consultas médicas","El copago que Fonasa o tu Isapre no te reembolsa.","salud"),
        ("Exámenes de diagnóstico","Laboratorio e imágenes, según el plan que elijas.","soap"),
        ("Medicamentos","Reembolso de receta médica, según el plan.","users"),
        ("Sin pasar por hospitalización","La cobertura opera en atención ambulatoria.","headset"))),

dict(slug="salud-hospitalario", bu="salud", tipo="producto",
     title="Seguro Hospitalario | Cotiza y compara online | Compara",
     desc="Seguro Hospitalario: cobertura para gastos de hospitalización y cirugía. Compara las alternativas del mercado y cotiza online en Compara.",
     h1='Seguro <span class="dserif">Hospitalario</span>',
     sub="Cobertura para gastos de hospitalización y cirugía. Compara las alternativas del mercado y elige la que te sirve.",
     cta="Cotiza tu Seguro Hospitalario",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Compara las alternativas de cobertura hospitalaria y elige.",
     coberturas=cob(
        ("Hospitalización","Días cama y atención durante la internación.","salud"),
        ("Cirugías","Honorarios y pabellón, según el plan que elijas.","soap"),
        ("Urgencias","Atención de urgencia cubierta.","siren"),
        ("Complemento a tu Isapre","Cubre lo que Fonasa o tu Isapre no reembolsa.","headset"))),

dict(slug="salud-oncologico", bu="salud", tipo="producto",
     title="Seguro Oncológico | Cotiza y compara online | Compara",
     desc="Seguro Oncológico: cobertura específica para diagnóstico y tratamiento de cáncer. Compara las alternativas del mercado y cotiza online.",
     h1='Seguro <span class="dserif">Oncológico</span>',
     sub="Cobertura específica para diagnóstico y tratamiento oncológico. Compara las alternativas del mercado y elige.",
     cta="Cotiza tu Seguro Oncológico",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Compara las alternativas de cobertura oncológica y elige.",
     coberturas=cob(
        ("Gastos de alto costo","Tope anual de hasta 30.000 UF, el rango en que suele caer un tratamiento oncológico.","salud"),
        ("Hospitalización","Cubierta ante enfermedades de alto costo.","siren"),
        ("Exámenes de laboratorio e imagenología","Incluidos dentro de la cobertura.","soap"),
        ("Complemento a tu Isapre","Cubre lo que Fonasa o tu Isapre no reembolsa.","headset"))),

dict(slug="salud-maternidad", bu="salud", tipo="producto",
     title="Seguro de Maternidad | Cotiza y compara online | Compara",
     desc="Seguro de Maternidad: cobertura para el parto y la atención asociada al embarazo. Compara las alternativas del mercado y cotiza online.",
     h1='Seguro de <span class="dserif">Maternidad</span>',
     sub="Cobertura para el parto y la atención asociada al embarazo. Compara las alternativas del mercado y elige.",
     cta="Cotiza tu Seguro de Maternidad",
     closer_ed="Sin letra chica, sin sorpresas.",
     closer_h2="Compara las alternativas de cobertura de maternidad y elige.",
     coberturas=cob(
        ("Parto y atención del embarazo","Lo que tu Isapre no reembolsa completo.","salud"),
        ("Controles y exámenes prenatales","Según el plan que elijas.","soap"),
        ("Hospitalización del parto","Días cama y pabellón.","siren"),
        ("Recién nacido","Cobertura del bebé, según las condiciones del plan.","users"))),

# ---------- COMPAÑÍAS DE VIDA (7) ----------
dict(slug="vida-consorcio", bu="vida", tipo="cia", marca="Consorcio",
     logo="logo_Consorcio.svg",
     title="Seguro de Vida Consorcio | Cotiza online | Compara",
     desc="Seguro de Vida Consorcio: capital asegurado de hasta 3.000 UF, planes temporales de 10 y 20 años y precio fijo durante la vigencia. Cotiza online.",
     h1='Seguro de Vida <span class="dserif">Consorcio</span>',
     sub="Capital asegurado de hasta 3.000 UF y precio fijo durante toda la vigencia del plan. Protege a quienes más quieres.",
     cta="Cotiza tu Seguro de Vida",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda Consorcio frente al resto del mercado.",
     coberturas=cob(
        ("Muerte por enfermedad y accidental","Las dos coberturas incluidas.","vida"),
        ("Invalidez permanente","Incluida en el plan.","users"),
        ("Capital asegurado","Hasta 3.000 UF.","soap"),
        ("Planes temporales","De 10 y 20 años, con precio fijo durante toda la vigencia.","headset"),
        ("Duración de la cobertura","Hasta los 65 años y 364 días.","siren"))),

dict(slug="vida-bci", bu="vida", tipo="cia", marca="BCI Seguros",
     logo="logo_Bci.svg",
     title="Seguro de Vida BCI Seguros | Cotiza online | Compara",
     desc="Seguro de Vida BCI Seguros: muerte por enfermedad, muerte accidental e invalidez permanente, con cobertura hasta los 69 años. Cotiza online.",
     h1='Seguro de Vida <span class="dserif">BCI Seguros</span>',
     sub="Compara y elige el mejor Seguro de Vida para proteger a quienes más quieres.",
     cta="Cotiza tu Seguro de Vida",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda BCI Seguros frente al resto del mercado.",
     coberturas=cob(
        ("Muerte por enfermedad","Cobertura base del plan.","vida"),
        ("Muerte accidental","Incluida en el plan.","siren"),
        ("Invalidez permanente","Incluida en el plan.","users"),
        ("Duración de la cobertura","Hasta los 69 años y 364 días.","headset"))),

dict(slug="vida-mapfre", bu="vida", tipo="cia", marca="Mapfre",
     logo="logo_Mapfre.svg",
     title="Seguro de Vida Mapfre | Cotiza online | Compara",
     desc="Seguro de Vida Mapfre: cobertura de hasta 4.000 UF ante muerte por enfermedad, muerte accidental e invalidez permanente. Cotiza online en Compara.",
     h1='Seguro de Vida <span class="dserif">Mapfre</span>',
     sub="Cobertura de hasta 4.000 UF para proteger a quienes más quieres. Compara y elige.",
     cta="Cotiza tu Seguro de Vida",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda Mapfre frente al resto del mercado.",
     coberturas=cob(
        ("Muerte por enfermedad","Cobertura base del plan.","vida"),
        ("Muerte accidental","Incluida en el plan.","siren"),
        ("Invalidez permanente","Incluida en el plan.","users"),
        ("Cobertura de hasta 4.000 UF","Duración hasta los 65 años y 364 días.","headset"))),

dict(slug="vida-metlife", bu="vida", tipo="cia", marca="MetLife",
     logo="logo_MetLife.png",
     title="Seguro de Vida MetLife | Cotiza online | Compara",
     desc="Seguro de Vida MetLife con ahorro: el 50% de tu prima se acumula con 1% de rentabilidad garantizada más UF, con hasta 4 retiros al año. Cotiza online.",
     h1='Seguro de Vida <span class="dserif">MetLife</span>',
     sub="Protege a quienes más quieres y acumula ahorro con rentabilidad garantizada.",
     cta="Cotiza tu Seguro de Vida",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda MetLife frente al resto del mercado.",
     coberturas=cob(
        ("Muerte por enfermedad y accidental","Las dos coberturas incluidas.","vida"),
        ("50% de tu prima como ahorro","Con 1% de rentabilidad garantizada más el crecimiento de la UF.","soap"),
        ("Hasta 4 retiros del ahorro por año","Disponibilidad sin esperar el fin del plan.","users"),
        ("Duración de la cobertura","Hasta los 64 años y 364 días.","headset"))),

dict(slug="vida-ap-southbridge", bu="vida", tipo="cia", marca="Southbridge",
     logo="logo_Southbridge.png",
     title="Seguro de Accidentes Personales Southbridge | Cotiza online | Compara",
     desc="Seguro de Accidentes Personales Southbridge: fallecimiento por accidente e invalidez permanente, con prima mensual fija. Cotiza online en Compara.",
     h1='Seguro de Accidentes Personales <span class="dserif">Southbridge</span>',
     sub="Fallecimiento por accidente e invalidez permanente, con prima mensual fija. Compara y elige.",
     cta="Cotiza tu Seguro de Accidentes Personales",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda Southbridge frente al resto del mercado.",
     coberturas=cob(
        ("Fallecimiento por accidente","Cobertura base del plan.","siren"),
        ("Invalidez permanente","Incluida en el plan.","users"),
        ("Prima mensual fija","No sube durante la vigencia.","soap"),
        ("Duración de la cobertura","Hasta los 69 años y 364 días.","headset"))),

dict(slug="vida-augustar", bu="vida", tipo="cia", marca="AuguStar",
     logo="logo_AuguStar.png",
     title="Seguro de Vida AuguStar | Cotiza online | Compara",
     desc="Seguro de Vida AuguStar: temporal a 5 años, capital asegurado de 2.000 UF y precio fijo durante toda la vigencia, desde 0,43 UF al mes. Cotiza online.",
     h1='Seguro de Vida <span class="dserif">AuguStar</span>',
     sub="Temporal a 5 años, con capital asegurado de 2.000 UF y precio fijo durante toda la vigencia. Desde 0,43 UF al mes.",
     cta="Cotiza tu Seguro de Vida",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda AuguStar frente al resto del mercado.",
     # Coberturas del plan que comercializamos, pasadas por Aroldo (2026-07-29).
     coberturas=cob(
        ("Seguro de vida temporal a 5 años","Con capital asegurado de 2.000 UF.","vida"),
        ("Fallecimiento por enfermedad y por accidente","Las dos coberturas incluidas.","siren"),
        ("Precio fijo","No sube durante toda la vigencia de la póliza.","soap"),
        ("Desde 0,43 UF al mes","El valor exacto lo ves al cotizar.","headset"))),

dict(slug="vida-chubb", bu="vida", tipo="cia", marca="Chubb",
     logo="logo_Chubb.png",
     title="Seguro de Vida Chubb | Cotiza online | Compara",
     desc="Seguro de Vida Chubb: capital asegurado de 1.000 o 2.000 UF, cobertura por fallecimiento por enfermedad y accidente, desde 0,19 UF al mes. Cotiza online.",
     h1='Seguro de Vida <span class="dserif">Chubb</span>',
     sub="Capital asegurado a tu elección y cobertura por fallecimiento por enfermedad o accidente, desde 0,19 UF al mes.",
     cta="Cotiza tu Seguro de Vida",
     closer_ed="Compara antes de decidir.",
     closer_h2="Mira cómo queda Chubb frente al resto del mercado.",
     # Coberturas del plan que comercializamos, pasadas por Aroldo (2026-07-29).
     # Precio en UF y no en CLP a propósito: el peso varía y la landing quedaría vieja.
     # El beneficio de streaming NO se menciona: no está en todos los planes, y prometerlo
     # en la landing de la marca genera reclamo si el plan que contrata no lo trae.
     coberturas=cob(
        ("Capital asegurado a tu elección","1.000 UF o 2.000 UF.","soap"),
        ("Fallecimiento por enfermedad y por accidente","Las dos coberturas incluidas.","vida"),
        ("Invalidez permanente 2/3","Disponible como cobertura adicional, en los planes con invalidez.","users"),
        ("Vigencia","Hasta los 75 años en el plan solo vida, hasta los 65 en el plan con invalidez.","headset"))),

# ---------- COMPAÑÍAS DE MASCOTAS (1) ----------
dict(slug="mascotas-bci", bu="mascotas", tipo="cia", marca="BCI Seguros",
     logo="logo_Bci.svg",
     title="Seguro de Mascotas BCI Seguros | Cotiza online | Compara",
     desc="Seguro de Mascotas BCI Seguros: cobertura veterinaria ante accidentes o enfermedades, sin deducible y con responsabilidad civil hasta 150 UF. Cotiza online.",
     h1='Seguro de Mascotas <span class="dserif">BCI Seguros</span>',
     sub="Cobertura veterinaria ante accidentes o enfermedades, sin deducible. Cotiza y elige el mejor plan para tu mascota.",
     cta="Cotiza el seguro de tu mascota",
     closer_ed="Sin letra chica, sin sorpresas.",
     # BCI es hoy la única compañía de Mascotas del comparador, así que "compáralo con el
     # resto del mercado" suena vacío. El closer y la sección "Por qué" van por el lado de
     # por qué contratarlo acá (hechos de nuestra página de producto).
     closer_h2="Contrata el seguro de tu mascota en minutos.",
     porque_h2="Por qué contratar BCI en Compara",
     porque_sub="Lo que ganas al contratarlo con nosotros.",
     porque=cob(
        ("100% online","Cotizas, eliges y contratas sin salir de tu casa.","headset"),
        ("Sin examen veterinario previo","Basta con los datos de tu mascota.","salud"),
        ("Sin deducible","No asumes un monto antes de que opere el reembolso.","soap"),
        ("Cancelación gratuita","Puedes dar de baja el plan sin costo.","users")),
     coberturas=cob(
        ("Reembolso de gastos médicos","Cobertura veterinaria ante accidentes o enfermedades.","salud"),
        ("Responsabilidad civil","Hasta 150 UF anuales.","users"),
        ("Sin deducible","Y telemedicina veterinaria incluida.","soap"),
        ("Urgencias y traslado","Más descuentos en medicamentos con receta, y baño, pet sitter y prevención según el plan.","headset"))),
]

# ============================================================================
# PLANTILLA
# ============================================================================
def cuadrado(logo):
    """Marcas cuadradas o casi (aspect < 1,3) llevan clase propia. Ver knowledge/logos.md."""
    return ' class="logo-mark--cuadrado"' if logo in ("logo_Bupa.svg",) else ""

def build(d):
    bu, tipo = d["bu"], d["tipo"]
    form = FORM[bu]
    cta = d["cta"]

    # --- hero figure: logo de la compañía (cia) o Comparini + plaquita (core/producto)
    if tipo == "cia":
        figura = f'''    <div class="hero-figure hero-figure--marca hero-enter" style="--i:2">
      <span class="marca-card"><img{cuadrado(d["logo"])} src="brand/design-system/assets/{d["logo"]}" alt="{d["marca"]}"></span>
    </div>'''
    else:
        s, st, sp = PLAQUITA_SLUG.get(d["slug"], PLAQUITA[bu])
        figura = f'''    <a class="hero-figure hero-figure-link hero-figure--salud hero-enter" style="--i:2" href="{form}" data-cotiza aria-label="{cta}">
      <img src="{HERO_IMG[bu]}" alt="{d["title"].split("|")[0].strip()} en Compara" onerror="this.style.display='none'">
      <span class="hero-offer-card" aria-hidden="true">
        <small>{s}</small>
        <strong>{st}</strong>
        <span>{sp}</span>
      </span>
    </a>'''

    # --- fila de aseguradoras: solo core/producto (en LP de marca resta foco)
    if tipo == "cia" or not INSURERS.get(bu):
        insurers = '''<!--
  ================= ASEGURADORAS — OMITIDA A PROPÓSITO =================
  En landing de compañía: mostrar la fila de competidores resta foco al único
  objetivo de conversión; el logo de la marca vive en el hero.
  En landing core sin fila: el BU todavía no tiene suficientes compañías en el
  comparador para sostener el copy de comparación (ver INSURERS en generate.py).
-->'''
    else:
        caps = "\n".join(
            f'      <span class="logo-capsule reveal" style="--i:{i}"><img{cuadrado(l)} src="brand/design-system/assets/{l}" alt="{alt}"></span>'
            for i,(l,alt,_) in enumerate(INSURERS[bu]))
        insurers = f'''<!-- ================= ASEGURADORAS ================= -->
<section class="insurers" id="aseguradoras">
  <div class="container">
    <h2 class="reveal">Comparas entre las aseguradoras <b>más importantes de Chile</b></h2>
    <p class="insurers-sub reveal" style="--i:1">Un solo lugar para ver todas tus opciones</p>
  </div>
  <div class="logo-rail">
    <!-- logo-cloud--fit: cápsula y slot fijos + object-fit:contain. Sin --ls por logo.
         Set tomado de los adgroups activos en Google Ads, pendiente de confirmar con Aroldo. -->
    <div class="logo-cloud logo-cloud--fit" id="logoCloud">
{caps}
    </div>
  </div>
</section>'''

    # --- pasos
    pasos = "\n".join(f'''      <div class="step reveal scrub" style="--i:{i}">
        <span class="step-n" aria-hidden="true"></span>
        <h3>{t}</h3>
        <p>{p}</p>
      </div>''' for i,(t,p) in enumerate(PASOS[bu]))

    # --- coberturas (o TODO visible si no hay contenido confirmado)
    if d["coberturas"] is None:
        todo = "\n".join(f'''      <div class="benefit reveal" style="--i:{i}">
        <span class="benefit-ico"><img src="brand/design-system/assets/{ICO['salud' if bu=='salud' else ('vida' if bu=='vida' else 'salud')]}" alt=""></span>
        <div>
          <h3>[TODO AROLDO] Cobertura {i+1}</h3>
          <p>Título corto + una línea de descripción.</p>
        </div>
      </div>''' for i in range(3))
        cobs = f'''<!-- TODO AROLDO — CONTENIDO PENDIENTE: las coberturas de este producto/compañía
     no existen en ninguna LP publicada hoy, así que NO se inventaron. Reemplazar los
     3 bloques de abajo con título + una línea cada uno. -->
{todo}'''
    else:
        cobs = "\n".join(f'''      <div class="benefit reveal" style="--i:{i}">
        <span class="benefit-ico"><img src="brand/design-system/assets/{c["i"]}" alt=""></span>
        <div>
          <h3>{c["t"]}</h3>
          <p>{c["d"]}</p>
        </div>
      </div>''' for i,c in enumerate(d["coberturas"]))

    # Sección extra opcional "Por qué X": para compañías donde no tenemos el detalle del
    # plan (usamos hechos institucionales del sitio oficial) y para el caso de una BU con
    # una sola compañía, donde "compáralo con el resto del mercado" suena vacío.
    porque = ""
    if d.get("porque"):
        items = "\n".join(f'''      <div class="benefit reveal" style="--i:{i}">
        <span class="benefit-ico"><img src="brand/design-system/assets/{p["i"]}" alt=""></span>
        <div>
          <h3>{p["t"]}</h3>
          <p>{p["d"]}</p>
        </div>
      </div>''' for i,p in enumerate(d["porque"]))
        porque = f'''
<!-- ================= POR QUÉ (hechos institucionales, no coberturas de plan) ================= -->
<section class="benefits section" id="por-que">
  <div class="container">
    <h2 class="reveal">{d["porque_h2"]}</h2>
    <p class="benefits-sub reveal" style="--i:1">{d["porque_sub"]}</p>
    <div class="benefits-grid">
{items}
    </div>
  </div>
</section>
'''

    # Título de la sección de coberturas. cob_h2_custom lo sobreescribe: se usa cuando la
    # sección no describe el plan de la compañía sino el producto genérico (AuguStar, Chubb).
    cob_h2 = d.get("cob_h2_custom") or ("Coberturas que te protegen de <span class=\"dserif\">verdad</span>"
              if tipo != "cia" else
              f"Qué cubre el {d['h1'].replace(chr(60)+'br'+chr(62),' ')}".replace('<span class="dserif">','').replace('</span>',''))
    cob_sub = d.get("cob_sub_custom") or ("Elige qué incluir según lo que necesitas. Te mostramos todo, también lo que no cubre."
               if tipo != "cia" else
               "El detalle del plan, sin letra chica. Compáralo con el resto del mercado antes de decidir.")

    origen = ("compañía: hero con el logo de la marca, sin fila de aseguradoras"
              if tipo=="cia" else f"{tipo}: hero con Comparini + plaquita, con fila de aseguradoras")

    return f'''<!--
  ============================================================================
  {d["title"].split("|")[0].strip().upper()}  ·  BU: {bu.upper()}  ·  tipo: {tipo}
  ============================================================================
  Generada por _docs/generate.py con el patrón "landing puente" validado en el
  piloto de Salud. Variante de {origen}.
  Editar el contenido en _docs/generate.py y regenerar, no a mano acá.
-->
<!doctype html>
<html lang="es" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{d["title"]}</title>
<meta name="description" content="{d["desc"]}">
<link rel="icon" href="brand/design-system/assets/avatar_favicon.svg">
<link rel="stylesheet" href="brand/design-system/colors_and_type.css">
<script>document.documentElement.classList.replace('no-js','js')</script>
<link rel="stylesheet" href="shared/compara.css?v={VER}">
</head>
<body>
<a class="skip-link" href="#main">Saltar al contenido</a>

<!-- ================= NAV (minimal — patrón "landing puente") ================= -->
<header class="nav nav--minimal" id="nav">
  <div class="container nav-inner">
    <a class="nav-logo" href="https://www.comparaonline.cl" aria-label="ComparaOnline, inicio">
      <img class="logo-white" src="brand/design-system/assets/logo_white.svg" alt="Compara">
      <img class="logo-blue" src="brand/design-system/assets/avatar_favicon.svg" alt="Compara">
      <img class="logo-compa" src="assets/bc-compa-feliz.svg" alt="Compara">
    </a>
    <!-- CTA del nav oculto a propósito. No borrar, solo descomentar si el negocio lo pide:
    <div class="nav-cta"><a class="btn btn--nav" href="https://www.compara.ai/">Conversemos de seguros</a></div>
    -->
  </div>
</header>

<main id="main">

<!-- ================= HERO (un solo CTA → formulario) ================= -->
<section class="hero hero--split" id="hero">
  <div class="wash wash--a" aria-hidden="true"></div>
  <div class="wash wash--b" aria-hidden="true"></div>
  <div class="hero-glow" id="heroGlow" aria-hidden="true"></div>

  <div class="hero-content">
    <div class="hero-copy">
      <h1 class="hero-enter" style="--i:0">{d["h1"]}</h1>
      <p class="hero-sub hero-enter" style="--i:1">{d["sub"]}</p>
      <div class="hero-cta hero-enter" style="--i:2">
        <!-- El texto del CTA se repite IDÉNTICO en sus 4 apariciones. -->
        <a class="btn btn--white btn--lg" href="{form}" data-cotiza>{cta}</a>
      </div>
      <div class="hero-trust hero-enter" style="--i:3">
{chr(10).join(f'        <span><i data-lucide="check" class="ico"></i>{t}</span>' for t in TRUST[bu])}
      </div>
    </div>
{figura}
  </div>
</section>

<!--
  ================= BANNER PROMOCIONAL — ELIMINADO A PROPÓSITO =================
  Sin promoción vigente confirmada. Según docs/02 paso 2.5, cuando no hay oferta
  activa se borra la sección completa, no se deja vacía. Si aparece una promo:
  recuperar el bloque desde _docs/template-landing-producto.html (necesita imagen
  desktop + mobile y el PDF de condiciones en Cloudinary, NO en el File Manager).
-->

{insurers}

<!-- ================= CÓMO FUNCIONA ================= -->
<section class="how section" id="como-funciona">
  <div class="container">
    <h2 class="reveal">Cotizar es así de <span class="dserif">simple</span></h2>
    <p class="how-lead reveal" style="--i:1">Sin llamadas eternas ni trámites imposibles. Cotizas online y te acompañamos en cada paso.</p>
    <div class="steps">
{pasos}
    </div>
  </div>
</section>

<!-- ================= COBERTURAS ================= -->
<section class="benefits section" id="coberturas">
  <div class="container">
    <h2 class="reveal">{cob_h2}</h2>
    <p class="benefits-sub reveal" style="--i:1">{cob_sub}</p>
    <div class="benefits-grid">
{cobs}
    </div>
  </div>
</section>
{porque}
<!-- ================= CTA FINAL ================= -->
<section class="closer section">
  <div class="container">
    <span class="editorial reveal">{d["closer_ed"]}</span>
    <h2 class="reveal" style="--i:1">{d["closer_h2"]}</h2>
    <a class="btn btn--primary btn--lg reveal" style="--i:2" href="{form}" data-cotiza>{cta}</a>
  </div>
</section>

</main>

<!-- ================= FOOTER ================= -->
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="brand/design-system/assets/logo_white.svg" alt="Compara">
        <p>La plataforma para comparar y contratar seguros con total transparencia.</p>
      </div>
      <div>
        <h3>Seguros</h3>
        <ul>
          <li><a href="auto.html">Seguro de Auto</a></li>
          <li><a href="salud.html">Seguro de Salud</a></li>
          <li><a href="vida.html">Seguro de Vida</a></li>
          <li><a href="mascotas.html">Seguro de Mascotas</a></li>
        </ul>
      </div>
      <div>
        <h3>Sobre nosotros</h3>
        <ul>
          <li><a href="https://www.comparaonline.cl">Quiénes somos</a></li>
          <li><a href="https://www.comparaonline.cl">Centro de ayuda</a></li>
        </ul>
      </div>
      <div>
        <h3>Países</h3>
        <ul>
          <li><a href="https://www.comparaonline.cl">Chile</a></li>
          <li><a href="https://www.comparaonline.com.br">Brasil</a></li>
          <li><a href="https://www.comparaonline.com.co">Colombia</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 ComparaOnline</span>
      <span class="spacer"></span>
      <a href="https://www.comparaonline.cl">Términos y condiciones</a>
      <a href="https://www.comparaonline.cl">Política de privacidad</a>
    </div>
  </div>
</footer>

<!-- CTA sticky (solo mobile): aparece al perder de vista el CTA del hero -->
<div class="cta-sticky">
  <a class="btn btn--primary btn--lg" href="{form}" data-cotiza>{cta}</a>
</div>

<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js" defer></script>
<script src="shared/compara.js?v={VER}" defer></script>
<script>
/* Redirección de los CTA al formulario de cotización de este producto.
   Conserva gclid / utm_* del clic SEM para no perder atribución de paid. */
(function(){{
  var FORM = '{form}';
  if (FORM === '#') return;
  var qs = location.search;
  document.querySelectorAll('[data-cotiza]').forEach(function(a){{
    a.href = FORM + (qs ? (FORM.indexOf('?') > -1 ? '&' : '?') + qs.slice(1) : '');
  }});
}})();
</script>
</body>
</html>
'''

if __name__ == "__main__":
    slugs = [d["slug"] for d in LANDINGS]
    assert len(slugs) == len(set(slugs)), "slug duplicado"
    pend, froz, gen = [], [], 0
    for d in LANDINGS:
        if d.get("frozen"):
            froz.append(d["slug"])
            print(f"  {d['slug']+'.html':<30} {d['tipo']:<9} {d['bu']:<9}  CONGELADA (no se toca)")
            continue
        (ROOT/f"{d['slug']}.html").write_text(build(d), encoding="utf-8")
        gen += 1
        flag = ""
        if d["coberturas"] is None:
            pend.append(d["slug"]); flag = "  <-- coberturas TODO"
        print(f"  {d['slug']+'.html':<30} {d['tipo']:<9} {d['bu']:<9}{flag}")
    print(f"\n{len(LANDINGS)} landings en el catálogo · {gen} generadas · {len(froz)} congeladas")
    if froz:
        print(f"congeladas (en revisión, ver comentario en el catálogo): {', '.join(froz)}")
    if pend:
        print(f"{len(pend)} con coberturas pendientes de contenido: {', '.join(pend)}")
