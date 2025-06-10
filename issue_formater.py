import json

def load_challenges(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_template(template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()
    
def fill_template(template, data):
    return template.format(**data)

def delivery_message(dates_review, challenges):
    check_delivery_status = sum(dates_review)
    if check_delivery_status == 0:
        return "❌ Incumplido"
    elif check_delivery_status < challenges:
        return "⚠️ Observado "
    return "✅"

def qty_status_files(files_status, expected_files):
    files_in_format = sum(files_status)
    missing_files = expected_files - files_in_format
    return missing_files, files_in_format

def qty_observed_files(files_status, dates_review):
    ok_files =sum(files_status and dates_review)
    available_files = sum(files_status)
    return available_files - ok_files

def folder_format(files_in_format, expected_files):
    if files_in_format == 0:
        return "❌ No se encontró ningún archivo"
    if files_in_format > 0 and files_in_format < expected_files:
        return "⚠️ No se encontró algunos archivos"
    return "✅ Correcta"

def issue_detail(files_status, dates_review, paths):
    message = []
    for i in range(len(paths)):
        file = paths[i]
        if "/" in paths[i]:
            file = paths[i].split("/")[1]
        
        status = "👀 Archivo encontrado"
        comment = "😅 Revisión pendiente"
        if not files_status[i]:
            status = "❌ No se encontró el archivo"
            comment = "😢"
        elif not dates_review[i]:
            status = "⚠️ Observado"
            comment = "Entregados fuera de fecha"
            
        issue_message = f" \n#### 🧩 Reto {i+1} – `{file}`\
            \n{status} \n💬 Comentario: {comment} \n "
        message.append(issue_message)
        
    return "".join(message)

def obs_last_message(missing_files, expected_files, observed_files):
    message = "**¿Realizaste cambios de formato?** Comenta este *issue* para solicitar una nueva revisión."
        
    if missing_files == expected_files:
        obs = "- ❌ No se encontró ningún reto de esta sesión 😢.\
         \n- ➡️ Si crees que este fue un **error** revisa que tu carpeta y archivos cumplan en formato solicitado."
    if missing_files < expected_files:
        obs = "- 🤓 Revisión pendiente.\
        \n- ⚠️ No encontramos algunos retos.\
        \n- ➡️ Si crees que este fue un **error** revisa que tu carpeta y archivos cumplan en formato solicitado."
    if missing_files == 0:
        obs = "- 🤓 Revisión pendiente."
        message = "Aún no concluimos la revisión 😅 Gracias por tu paciencia."
    if observed_files > 0:
        obs = "- 🤓 Revisión pendiente.\
            \n- ⚠️ Los retos presentados fuera de plazo no cuentan para tu calificación."
        message = "Aún no concluimos la revisión 😅 Gracias por tu paciencia. Comenta este *issue* si tienes alguna duda, consulta o reclamo."
    return obs, message
    
def summary_preview(files_status, dates_review, reto_data):
    tmplt_data={}
    challenges = reto_data["challenges"]
    expected_files = reto_data["expected_files"]
    paths = reto_data["paths"]
    
    tmplt_data["challenges"] = challenges
    tmplt_data["expected_files"] = expected_files
    
    template_path = "templates/dynamic_format.md"
    
    tmplt_data["delivery_status"] = delivery_message(dates_review, challenges)
    
    missing_files, files_in_format = qty_status_files(files_status, expected_files)
    format_message = folder_format(files_in_format, expected_files)
    feedback_challenges = issue_detail(files_status, dates_review, paths)
    tmplt_data["missing_files"] = missing_files
    tmplt_data['files_in_format'] = files_in_format
    tmplt_data['folder_format'] = format_message
    
    observed_files = qty_observed_files(files_status, dates_review)
    tmplt_data['observed_files'] = observed_files
    
    tmplt_data['feedback_challenges'] = feedback_challenges
    
    obs, final_message = obs_last_message(missing_files, expected_files, observed_files)
    tmplt_data["obs_list"] = obs
    tmplt_data["final_message"] = final_message
    
    template = load_template(template_path)
    issue_content = fill_template(template, tmplt_data)
    
    return issue_content 
    
