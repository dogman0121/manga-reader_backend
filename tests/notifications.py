from app.notifications.models import Notification
from app.user.models import User

def test_getting_notification(app, client, jwt_token):
    user = User(login="c", email="bibi@mail.ru", password="12345678")
    actor = User(login="d", email="baba@mail.ru", password="12345678")
    user.add()
    actor.add()

    notification = Notification(
        action="subscribe",
        user=user,
        actor=actor
    )
    notification.add()

    response = client.get("/api/v1/notifications", headers={"Authorization": f"Bearer {jwt_token}"})

    assert response.status_code == 200
    assert response.json["data"] != []
    assert response.json["data"][0]["type"] == "user"



