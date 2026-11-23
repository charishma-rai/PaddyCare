import sys, tempfile
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from webapp import db


def test_flow():
    db.configure(tempfile.mkdtemp()); db.init()
    ok, _ = db.create_user("Asha K", "asha_1", "secret1", "Farmer", "Udupi", "999")
    assert ok
    assert not db.create_user("X", "asha_1", "secret1", "Farmer")[0]          # duplicate username
    assert not db.create_user("X", "ab", "secret1", "Farmer")[0]              # short username
    assert db.authenticate("asha_1", "wrong") is None
    u = db.authenticate("ASHA_1", "secret1"); assert u and u["name"] == "Asha K"
    db.add_prediction(u["id"], "Blast", 0.9, False, None)
    assert len(db.list_predictions(u["id"])) == 1 and len(db.list_predictions(u["id"], "Healthy")) == 0
    pid = db.add_post(u["id"], "Need help", "Help", "Spots on leaves", "Udupi", False)
    assert db.list_posts()[0]["contact"] is None                              # phone hidden unless shared
    pid2 = db.add_post(u["id"], "Sell produce", "Paddy", "10 quintal", "Udupi", True)
    assert db.list_posts("Sell produce")[0]["contact"] == "999"
    db.add_reply(pid, u["id"], "Try this"); assert db.list_posts(user_id=u["id"])[1]["n_replies"] == 1
    db.delete_post(u["id"], pid); assert len(db.list_posts()) == 1


if __name__ == "__main__":
    test_flow(); print("db tests passed")
