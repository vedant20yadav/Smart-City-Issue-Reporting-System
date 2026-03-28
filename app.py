from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# -------------------- App & MySQL Config --------------------
app.secret_key = 'smartcity'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql@123'
app.config['MYSQL_DB'] = 'smart_city'

mysql = MySQL(app)

# -------------------- Priority Logic --------------------
def assign_priority(category):
    if category in ['Road', 'Water', 'Electricity']:
        return 'High'
    elif category == 'Garbage':
        return 'Medium'
    else:
        return 'Low'

# -------------------- Routes --------------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        location = request.form['location']
        priority = assign_priority(category)

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO issues (category, description, location, priority) VALUES (%s, %s, %s, %s)",
            (category, description, location, priority)
        )
        mysql.connection.commit()
        cur.close()

        flash("Issue reported successfully!", "success")
        return redirect(url_for('report'))

    return render_template('report.html')


@app.route('/admin')
def admin():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM issues ORDER BY created_at DESC")
    issues = cur.fetchall()
    cur.close()
    return render_template('admin.html', issues=issues)


@app.route('/update_status', methods=['POST'])
def update_status():
    issue_id = request.form['issue_id']
    status = request.form['status']

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE issues SET status=%s WHERE id=%s",
        (status, issue_id)
    )
    mysql.connection.commit()
    cur.close()

    flash("Status updated successfully!", "success")
    return redirect(url_for('admin'))


@app.route('/delete_issue/<int:issue_id>', methods=['POST'])
def delete_issue(issue_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM issues WHERE id=%s", (issue_id,))
    mysql.connection.commit()
    cur.close()

    flash("Issue deleted successfully!", "success")
    return redirect(url_for('admin'))


@app.route('/analytics')
def analytics():
    cur = mysql.connection.cursor()

    cur.execute("SELECT category, COUNT(*) FROM issues GROUP BY category")
    category_data = cur.fetchall()

    cur.execute("SELECT priority, COUNT(*) FROM issues GROUP BY priority")
    priority_data = cur.fetchall()

    cur.close()

    categories = [row[0] for row in category_data]
    category_counts = [row[1] for row in category_data]

    priorities = [row[0] for row in priority_data]
    priority_counts = [row[1] for row in priority_data]

    return render_template(
        'analytics.html',
        categories=categories,
        category_counts=category_counts,
        priorities=priorities,
        priority_counts=priority_counts
    )


# -------------------- Run App --------------------
if __name__ == '__main__':
    app.run(debug=True)
    app.run(debug=True)
