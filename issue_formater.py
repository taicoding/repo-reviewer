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
    ok_files = sum(files_status and dates_review)
    available_files = sum(files_status)
    return available_files - ok_files


def folder_format(files_in_format, expected_files):
    if files_in_format == 0:
        return "❌ No se encontró ningún archivo"
    if files_in_format > 0 and files_in_format < expected_files:
        return "⚠️ No se encontró algunos archivos"
    return "✅ Correcta"


def qty_successful_tests(code_review):
    success = sum(1 for review in code_review if review[1].find("✔️") >= 0)
    return success


def no_file_issue_detail(fork_status, branch_status, activity_status):
    message = []
    summary = [
        {
            "status": fork_status,
            "comentario_ok": "Se verificó que el repositorio es un fork del [repositorio de retos](https://github.com/python-la-paz/psg-retos).",
            "comentario_fail": "El repositorio no es un fork del [repositorio de retos](https://github.com/python-la-paz/psg-retos).",
        },
        {
            "status": activity_status,
            "comentario_ok": "Se verificó que el repositorio fue clonado correctamente.",
            "comentario_fail": "No se detectó que el repositorio haya sido clonado.",
        },
        {
            "status": branch_status,
            "comentario_ok": "La rama con el nombre esperado existe en el repositorio.",
            "comentario_fail": "No se encontró una rama con el nombre esperado en el repositorio.",
        },
        {
            "status": activity_status,
            "comentario_ok": "Se verificó que la rama fue publicada en el repositorio.",
            "comentario_fail": "No se encontró la rama publicada en el repositorio.",
        },
    ]
    for i in range(len(summary)):
        status = (
            "✔️ Completado exitosamente." if summary[i]["status"] else "❌ Incumplido"
        )
        comment = (
            summary[i]["comentario_ok"]
            if summary[i]["status"]
            else summary[i]["comentario_fail"]
        )

        issue_message = f"\n#### 🧩 Reto {i+1}\
            \n{status} \n💬 Comentario: {comment} \n "
        message.append(issue_message)
    return "".join(message)


def file_issue_detail(files_status, dates_review, paths):
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


def code_review_detail(files_status, dates_review, code_review):
    message = []
    for i in range(len(code_review)):
        status = "❌ No se encontró el archivo"
        if not dates_review[i]:
            status = "❌ Entregados fuera de fecha"
        elif code_review[i][1].find("✔️") >= 0 and files_status[i] and dates_review[i]:
            status = code_review[i][1]
        elif code_review[i][1].find("❌") >= 0:
            status = code_review[i][1]
        issue_message = f" \n#### 🧩 {code_review[i][0]}\
                \n{status}\n"
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
    tmplt_data = {}
    challenges = reto_data["challenges"]
    expected_files = reto_data["expected_files"]
    paths = reto_data["paths"]

    tmplt_data["challenges"] = challenges
    tmplt_data["expected_files"] = expected_files

    template_path = "templates/dynamic_format.md"

    tmplt_data["delivery_status"] = delivery_message(dates_review, challenges)

    missing_files, files_in_format = qty_status_files(files_status, expected_files)
    format_message = folder_format(files_in_format, expected_files)
    feedback_challenges = file_issue_detail(files_status, dates_review, paths)
    tmplt_data["missing_files"] = missing_files
    tmplt_data["files_in_format"] = files_in_format
    tmplt_data["folder_format"] = format_message

    observed_files = qty_observed_files(files_status, dates_review)
    tmplt_data["observed_files"] = observed_files

    tmplt_data["feedback_challenges"] = feedback_challenges

    obs, final_message = obs_last_message(missing_files, expected_files, observed_files)
    tmplt_data["obs_list"] = obs
    tmplt_data["final_message"] = final_message

    template = load_template(template_path)
    issue_content = fill_template(template, tmplt_data)

    return issue_content


def summary_code_review(
    author,
    files_status,
    dates_review,
    no_code_status,
    code_review,
    reto_data,
    template_path,
):
    tmplt_data = {}
    challenges = reto_data["challenges"]
    expected_files = reto_data["expected_files"]
    points = reto_data["points"]
    tmplt_data["challenges"] = challenges
    tmplt_data["expected_files"] = expected_files
    tmplt_data["points"] = points

    missing_files, files_in_format = qty_status_files(files_status, expected_files)
    format_message = folder_format(files_in_format, expected_files)

    feedback_no_code = no_file_issue_detail(
        no_code_status[0], no_code_status[1], no_code_status[2]
    )
    feedback_challenges = code_review_detail(files_status, dates_review, code_review)

    code_success = qty_successful_tests(code_review)
    no_code_success = feedback_no_code.count("✔️")
    folder_success = int(files_in_format == expected_files) * 6

    total_success = code_success + no_code_success + folder_success

    tmplt_data["delivery_status"] = delivery_message(dates_review, expected_files)

    tmplt_data["missing_files"] = missing_files
    tmplt_data["files_in_format"] = files_in_format
    tmplt_data["folder_format"] = format_message
    tmplt_data["total_points"] = total_success

    tmplt_data["feedback_challenges"] = feedback_no_code + feedback_challenges

    tmplt_data["author"] = author

    template = load_template(template_path)
    issue_content = fill_template(template, tmplt_data)

    return issue_content
