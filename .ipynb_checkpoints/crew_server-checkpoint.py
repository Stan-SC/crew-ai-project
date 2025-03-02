from flask import Flask, render_template, Response
from crew_factory import CrewFactory
from datetime import datetime
import json
import queue
import threading

app = Flask(__name__)
updates_queue = queue.Queue()

class MonitoredCrewFactory(CrewFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = None
        
    def create_agent(self, name, role, goal, backstory):
        agent = super().create_agent(name, role, goal, backstory)
        # Surcharge de la méthode execute_task de l'agent pour monitorer les actions
        original_execute = agent.execute_task
        def monitored_execute(*args, **kwargs):
            response = original_execute(*args, **kwargs)
            # Envoi de la mise à jour au flux SSE
            update = {
                'agent': name,
                'action': 'working',
                'timestamp': datetime.now().isoformat(),
                'message': response if isinstance(response, str) else str(response)
            }
            updates_queue.put(json.dumps(update))
            return response
        agent.execute_task = monitored_execute
        return agent

def run_crew():
    factory = MonitoredCrewFactory()
    crew = factory.create_development_crew()
    updates_queue.put(json.dumps({
        'type': 'status',
        'message': 'Équipe créée, début du travail...'
    }))
    result = crew.kickoff()
    updates_queue.put(json.dumps({
        'type': 'complete',
        'message': result
    }))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            update = updates_queue.get()
            yield f"data: {update}\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Démarrage du thread pour l'exécution de l'équipe
    crew_thread = threading.Thread(target=run_crew)
    crew_thread.daemon = True
    crew_thread.start()
    
    # Utilisation du port 5001 au lieu de 5000
    app.run(debug=True, threaded=True, port=5001) 