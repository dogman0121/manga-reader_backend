from flask import jsonify

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