import os
import json
import boto3
import pdfkit

# Récup des params
BUCKET = os.environ['S3_BUCKET']
FROM = os.environ['FROM_EMAIL']
SES = boto3.client('ses', region_name=os.environ['AWS_REGION'])
S3  = boto3.client('s3',  region_name=os.environ['AWS_REGION'])

def main():
    # 1. Lire le HTML
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    # 2. Générer le PDF (nécessite wkhtmltopdf installé)
    pdf_bytes = pdfkit.from_string(html, False)

    # 3. Uploader sur S3
    key = 'itineraries/latest.pdf'
    S3.put_object(Body=pdf_bytes, Bucket=BUCKET, Key=key)
    # URL pré-signée (valable 1h)
    url = S3.generate_presigned_url('get_object',
                Params={'Bucket':BUCKET,'Key':key},
                ExpiresIn=3600)

    # 4. Envoyer l’email avec le lien
    SES.send_email(
        Source=FROM,
        Destination={'ToAddresses':[FROM]},  # tu peux remplacer par un destinataire différent
        Message={
            'Subject':{'Data':'Votre itinéraire est prêt'},
            'Body': {
                'Html':{'Data':f"<p>Bonjour,</p><p>Voici votre itinéraire : <a href='{url}'>Télécharger le PDF</a></p>"}
            }
        }
    )
    print("PDF généré, uploadé, et email envoyé.")

if __name__ == '__main__':
    main()
