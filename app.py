import boto3
import chalice
import os
import secrets


BUCKET_NAME = os.getenv("BUCKET_NAME") or "bytebin"
RESERVED_KEYS = ["post"]

app = chalice.Chalice(app_name="bytebin")


def token():
    s3 = boto3.client("s3")
    n = 2
    t = 0
    while True:
        k = secrets.token_urlsafe(n)
        if k not in RESERVED_KEYS:
            try:
                s3.head_object(Bucket=BUCKET_NAME, Key=k)
            except:
                return k
        if t > 2:
            n += 1
            t = 0
        else:
            t += 1


@app.route("/post", methods=["POST"])
def post():
    s3 = boto3.resource("s3")
    d = app.current_request.raw_body
    k = token()
    try:
        s3.Object(BUCKET_NAME, k).put(Body=d)
    except:
        r = chalice.Response("", status_code=503)
    else:
        r = chalice.Response({"key": k},
                             status_code=201,
                             headers={"Location": k})
    return r


@app.route("/{key}", methods=["GET"])
def object(key):
    s3 = boto3.resource("s3")
    o = s3.Object(BUCKET_NAME, key)
    try:
        o.load()
    except:
        r = chalice.Response("", status_code=404)
    else:
        try:
            r = o.get()
        except:
            r = chalice.Response("", status_code=404)
        else:
            r = r["Body"].read()
    return r
