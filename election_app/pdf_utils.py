from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from .models import ElectionRound, Candidate

def generate_results_pdf(request, round_id):
    # Get the election round and candidates
    try:
        election_round = ElectionRound.objects.get(id=round_id)
    except ElectionRound.DoesNotExist:
        return HttpResponse(f"Election round with ID {round_id} does not exist.", status=404)

    candidates = Candidate.objects.filter(election_round=election_round)

    # Prepare HTML content for the PDF
    html_content = render_to_string('pdf_template.html', {
        'election_round': election_round,
        'candidates': candidates
    })

    # Create a PDF from the HTML content
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('UTF-8')), pdf)

    if pisa_status.err:
        return HttpResponse('Error creating PDF', status=500)
    
    # Create a response and attach the generated PDF
    response = HttpResponse(pdf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{election_round.name}-results.pdf"'
    return response
