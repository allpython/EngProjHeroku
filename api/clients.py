import app
import helper

@app.route('/api/v1/clients')
@login_required
def list_clients():
    return helper.get_items(app.Client)
