from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Simulation, SimulationEvent, SimulationResponse
import json

def index(request):
    return render(request, 'index.html')




def trainer_dashboard(request):
    sim, created = Simulation.objects.get_or_create(id=1)
    events = SimulationEvent.objects.all().order_by('trigger_time_ms')
    responses = SimulationResponse.objects.filter(simulation=sim)
    
    context = {
        'sim': sim,
        'events': events,
        'responses': responses,
    }
    return render(request, 'trainer_dashboard.html', context)




def start_simulation(request):
    sim = Simulation.objects.get(id=1)
    if sim.status == 'READY':
        sim.status = 'RUNNING'
        sim.start_time = timezone.now()
        sim.paused_at = None
        sim.accumulated_time_ms = 0
        sim.save()
    return redirect('trainer_dashboard')




def reset_simulation(request):
    sim = Simulation.objects.get(id=1)
    SimulationResponse.objects.filter(simulation=sim).delete()
    sim.status = 'READY'
    sim.start_time = None
    sim.paused_at = None
    sim.accumulated_time_ms = 0
    sim.save()
    return redirect('index')



def pause_resume_simulation(request):
    sim = Simulation.objects.get(id=1)
    now = timezone.now()
    if sim.status == 'RUNNING':
        sim.status = 'PAUSED'
        if sim.paused_at:
            delta = now - sim.paused_at
        else:
            delta = now - sim.start_time    
        
        sim.accumulated_time_ms += int(delta.total_seconds() * 1000)
        sim.paused_at = now
    elif sim.status == 'PAUSED':
        sim.status = 'RUNNING'
        sim.paused_at = now
    sim.save()
    return redirect('trainer_dashboard')




def participant_view(request, role):
    sim = Simulation.objects.get(id=1)
    context = {
        'sim': sim,
        'role': role,
    }
    return render(request, 'participant_view.html', context)




def check_updates(request):
    sim = Simulation.objects.get(id=1)
    current_time = sim.current_sim_time_ms()
    role = request.GET.get('role')
    
    trigger_data = []
    event_statuses = []
    
    if role == 'TRAINER':
        all_events = SimulationEvent.objects.all()
        for event in all_events:
            resp = SimulationResponse.objects.filter(simulation=sim, event=event).first()
            status = 'Pending'
            if resp:
                if resp.is_missed: status = 'Missed'
                elif resp.choice is True: status = 'YES'
                elif resp.choice is False: status = 'NO'
            elif current_time > event.trigger_time_ms + 60000:
                status = 'Missed'
            
            event_statuses.append({
                'id': event.id,
                'status': status
            })
    else:
        events = SimulationEvent.objects.filter(role=role, trigger_time_ms__lte=current_time)
        for event in events:
            resp, created = SimulationResponse.objects.get_or_create(simulation=sim, event=event)
            if resp.choice is None and not resp.is_missed:
                if current_time - event.trigger_time_ms > 60000:
                    resp.is_missed = True
                    resp.save()
                else:
                    trigger_data.append({
                        'id': event.id,
                        'message': event.message,
                        'prompt': event.decision_prompt,
                        'time_left': 60 - int((current_time - event.trigger_time_ms)/1000)
                    })
    
    return JsonResponse({
        'status': sim.status,
        'sim_time': current_time,
        'triggers': trigger_data,
        'event_statuses': event_statuses
    })

def submit_decision(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sim = Simulation.objects.get(id=1)
        event = get_object_or_404(SimulationEvent, id=data.get('event_id'))
        resp = get_object_or_404(SimulationResponse, simulation=sim, event=event)
        
        if not resp.is_missed and resp.choice is None:
            resp.choice = data.get('decision') == 'YES'
            resp.responded_at_ms = sim.current_sim_time_ms()
            resp.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def report_view(request):
    sim = Simulation.objects.get(id=1)
    responses = SimulationResponse.objects.filter(simulation=sim).select_related('event')
    
    # the outcome logic
    it_esc = responses.filter(event__role='IT', choice=True).exists()
    legal_not = responses.filter(event__role='LEGAL', choice=True).exists()
    any_missed = responses.filter(is_missed=True).exists()
    
    outcome = "Breach Escalated"
    if it_esc and legal_not:
        outcome = "Contained"
    elif it_esc or legal_not:
        outcome = "Partially Contained"
    
    if any_missed:
        outcome = "Breach Escalated (Due to delayed response)"

    context = {
        'responses': responses,
        'outcome': outcome,
    }
    return render(request, 'report.html', context)
