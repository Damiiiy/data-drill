from django.core.management.base import BaseCommand
from core.models import SimulationEvent

class Command(BaseCommand):
    help = 'Seeds initial simulation events'

    def handle(self, *args, **kwargs):
        events = [
            {
                'role': 'IT',
                'trigger_time_ms': 2 * 60000,
                'message': 'CRITICAL: Server Alert - Patient records detected on public Pastebin.',
                'decision_prompt': 'Escalate to major incident?'
            },
            {
                'role': 'LEGAL',
                'trigger_time_ms': 5 * 60000,
                'message': 'Regulatory Inquiry - Fake regulator email regarding data leak.',
                'decision_prompt': 'Notify the regulator immediately?'
            },
            {
                'role': 'CEO',
                'trigger_time_ms': 8 * 60000,
                'message': 'Public Relations - Fake news headline: "Hospital Leaks Thousands of Records".',
                'decision_prompt': 'Issue a public statement now?'
            }
        ]

        for e_data in events:
            SimulationEvent.objects.get_or_create(
                role=e_data['role'],
                trigger_time_ms=e_data['trigger_time_ms'],
                defaults={
                    'message': e_data['message'],
                    'decision_prompt': e_data['decision_prompt']
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded simulation events'))
