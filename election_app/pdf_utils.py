import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import ElectionRound, Candidate, Vote
import os
from django.conf import settings

def generate_results_pdf(request, round_id):
    # Get the election round and candidates
    try:
        election_round = ElectionRound.objects.get(id=round_id)
    except ElectionRound.DoesNotExist:
        return HttpResponse(f"Election round with ID {round_id} does not exist.", status=404)

    # Retrieve candidates and calculate votes
    candidates = Candidate.objects.filter(election_round=election_round)
    total_votes = Vote.objects.filter(election_round=election_round).count()
    absent_votes = Vote.objects.filter(election_round=election_round, candidate=None).count()

    header_image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'header_image.jpg')


    # Prepare HTML content for the PDF with Thai font
    html_content = render_to_string('pdf_template.html', {
        'election_round': election_round,
        'candidates': candidates,
        'total_votes': total_votes,
        'absent_votes': absent_votes,
        'header_image': header_image_path,
        'request': request
    })

    # Set pdfkit options
    options = {
    'encoding': 'UTF-8',
    'enable-local-file-access': '',
    'quiet': '',
    'page-size': 'A4'
}

    # Path to wkhtmltopdf executable (update this path to the correct one)
    current_path = os.getcwd()
    path_wkhtmltopdf = os.path.join(current_path, 'utility', 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    try:
        # Generate PDF using pdfkit
        pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)

        # Create a response and attach the generated PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{election_round.name}-results.pdf"'
        return response
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)
