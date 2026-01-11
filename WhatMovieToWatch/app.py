from flask import Flask, render_template, request, redirect, url_for, session
from recommender import recommend_movies

app = Flask(__name__)
app.secret_key = "dev-secret"  # required for session


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        results = recommend_movies(
            occasion=request.form.get("occasion"),
            genres=request.form.getlist("genres"),
            mood=request.form.get("mood"),
            recency=request.form.get("recency"),
            top_n=10
        )

        # store results in session (convert to dict)
        session["results"] = results.to_dict("records")

        #redirect instead of render
        return redirect(url_for("index"))

    # GET request
    results = session.pop("results", None)
    return render_template("index.html", results=results)

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)
