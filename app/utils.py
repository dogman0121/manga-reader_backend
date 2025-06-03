from flask import jsonify, current_app

def respond(data=None, error=None, detail=None, status_code=200):
    if error:
        response = jsonify({
            "error": {
                "code": error,
                "detail": detail,
            }
        })
    else:
        response = jsonify({
            "data": data,
        })

    response.status_code = status_code

    return response


def create_link(path):
    server_name = current_app.config["SERVER_NAME"]
    use_ssl = current_app.config["USE_SSL"]

    if use_ssl:
        return "https://" + server_name + path
    else:
        return "http://" + server_name + path
