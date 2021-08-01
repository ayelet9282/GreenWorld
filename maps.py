from flask import Flask,render_template, request

app = Flask('__name__')
@app.route('/')
def index():
  if request.args.get("next") is None:
    return render_template("maps.html", num=0)
  elif int(request.args.get("next"))==14:
    return render_template("maps2.html")
  else:
    return render_template("maps.html", num=int(request.args.get("next"))+1)
if __name__ == '__main__':
  app.run()
