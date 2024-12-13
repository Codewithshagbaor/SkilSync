from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import WalletConnectionSerializer, ProfileSerializer, JobPreferenceSerializer, JobMatchSerializer
from coinbase.wallet.client import Client
from rest_framework.permissions import IsAuthenticated
from web3 import Web3
import json
from core.models import User
import secrets
from user_profile.models import Profile
from .utils import upload_to_pinata
import logging
import requests
import fitz  # PyMuPDF
import re
import tempfile
import os
from openai import OpenAI
logger = logging.getLogger(__name__)
def generate_nonce():
    """Generate a secure random nonce"""
    return secrets.token_hex(16)
class ConnectWalletView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = WalletConnectionSerializer(data=request.data)
        
        if serializer.is_valid():
            wallet_address = serializer.validated_data['wallet_address']
            user = request.user

            # Check if wallet address is already connected to another account
            if user.__class__.objects.filter(wallet_address=wallet_address).exclude(id=user.id).exists():
                return Response(
                    {'error': 'This wallet address is already connected to another account'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate secure nonce
            nonce = generate_nonce()
            
            # Update user
            user.wallet_address = wallet_address
            user.nonce = nonce
            user.save()

            return Response({
                'message': 'Wallet connected successfully',
                'wallet_address': wallet_address,
                'nonce': nonce
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Endpoint to disconnect wallet"""
        user = request.user
        if not user.wallet_address:
            return Response(
                {'error': 'No wallet connected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user.wallet_address = None
        user.nonce = None
        user.save()

        return Response({'message': 'Wallet disconnected successfully'})

    def get(self, request):
        """Endpoint to get current wallet connection status"""
        user = request.user
        if user.wallet_address:
            return Response({
                'connected': True,
                'wallet_address': user.wallet_address
            })
        return Response({'connected': False})

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the user's profile.
        """
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if 'resume' in request.FILES:
            resume = request.FILES['resume']
            try:
                logger.info("Uploading resume to Pinata...")
                upload_result = upload_to_pinata(resume)
                logger.info(f"Upload result: {upload_result}")
                
                # Modify request data to include the Pinata URL
                request.data['resume'] = upload_result
            except Exception as e:
                logger.error(f"Error uploading resume to Pinata: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Now validate the serializer with the updated data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class JobPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.profile
        serializer = JobPreferenceSerializer(user.jobpreference)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user.profile
        job_preferences = user.jobpreference
        serializer = JobPreferenceSerializer(job_preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UserSocialProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request, provider):
#         user = request.user
#         if provider == 'github':
#             if not user.github_url:
#                 return Response({'error': 'No GitHub URL found'}, status=status.HTTP_404_NOT_FOUND)
#             return Response({'url': user.github_url})
#         elif provider == 'linkedin':
#             if not user.linkedin_url:
#                 return Response({'error': 'No LinkedIn URL found'}, status=status.HTTP_404_NOT_FOUND)
#             return Response({'url': user.linkedin_url})
#         else:
#             return Response({'error': 'Invalid provider'}, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, provider):
#         user = request.user
#         if provider == 'github':
#             if not user.github_url:
#                 return Response({'error': 'No GitHub URL found'}, status=status.HTTP_404_NOT_FOUND)
#             user.github_url = request.data['url']
#             user.save()
#             return Response({'message': 'GitHub URL updated successfully'})
#         elif provider == 'linkedin':
#             if not user.linkedin_url:
#                 return Response({'error': 'No LinkedIn URL found'}, status=status.HTTP_404_NOT_FOUND)
#             user.linkedin_url = request.data['url']
#             user.save()
#             return Response({'message': 'LinkedIn URL updated successfully'})

# def get_user_social_profile_analytics(user):
#     """Get user social profile analytics"""
#     # Get GitHub analytics
#     github_analytics = get_github_analytics(user.github_url)
#     if not github_analytics:
#         github_analytics = {'followers': 0, 'following': 0, 'stars': 0, 'public_repos': 0}

#     # Get LinkedIn analytics
#     linkedin_analytics = get_linkedin_analytics(user.linkedin_url)
#     if not linkedin_analytics:
#         linkedin_analytics = {'connections': 0, 'connections_followed': 0, 'company_name': '', 'company_url': ''}

#     return {
#         'github_analytics': github_analytics,
#         'linkedin_analytics': linkedin_analytics
#     }

# def get_github_analytics(github_url):
#     """Get GitHub analytics"""
#     if not github_url:
#         return None
#     try:
#         # Get the user's GitHub username from the URL
#         username = github_url.split('/')[-2]
#         # Get the user's GitHub profile
#         response = requests.get(f'https://api.github.com/users/{username}')
#         if response.status_code == 200:
#             data = response.json()
#             # Extract the user's GitHub analytics
#             followers = data.get('followers')
#             following = data.get('following')
#             stars = data.get('public_repos')
#             public_repos = data.get('public_repos')
#             return {'followers': followers, 'following': following, 'stars': stars, 'public_repos': public_repos}
#         else:
#             return None
#     except Exception as e:
#         logger.error(f"Error getting GitHub analytics: {str(e)}")
#         return None

# def get_linkedin_analytics(linkedin_url):
#     """Get LinkedIn analytics"""
#     if not linkedin_url:
#         return None
#     try:
#         # Get the user's LinkedIn profile
#         response = requests.get(linkedin_url)
#         if response.status_code == 200:
#             data = response.json()
#             # Extract the user's LinkedIn analytics
#             connections = data.get('numConnections')
#             connections_followed = data.get('numConnectionsFollowed')
#             company_name = data.get('companyName')
#             company_url = data.get('companyUrl')
#             return {'connections': connections, 'connections_followed': connections_followed, 'company_name': company_name, 'company_url': company_url}
#         else:
#             return None
#     except Exception as e:
#         logger.error(f"Error getting LinkedIn analytics: {str(e)}")
#         return None
# class UserSocialProfileAnalyticsView(APIView):
#     permission_classes = [IsAuthenticated]

def analyze_github(github_url):
    """
    Fetch and analyze GitHub repositories and profile data.
    """
    username = github_url.split("/")[-1]  # Extract username from URL
    user_api_url = f"https://api.github.com/users/{username}"
    repos_api_url = f"https://api.github.com/users/{username}/repos"

    # Fetch user profile data
    user_response = requests.get(user_api_url)
    if user_response.status_code != 200:
        return {"error": "Failed to fetch GitHub user profile"}

    user_data = user_response.json()

    # Fetch repositories data
    repos_response = requests.get(repos_api_url)
    if repos_response.status_code != 200:
        return {"error": "Failed to fetch GitHub repositories"}

    repos = repos_response.json()

    # Process repositories
    languages = []
    popular_repos = []
    for repo in repos:
        languages.append(repo.get("language"))
        popular_repos.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "url": repo.get("html_url"),
        })

    # Sort repositories by popularity (stars)
    popular_repos = sorted(popular_repos, key=lambda x: x["stars"], reverse=True)[:5]

    return {
        "username": user_data.get("login"),
        "name": user_data.get("name"),
        "bio": user_data.get("bio"),
        "location": user_data.get("location"),
        "public_repos_count": user_data.get("public_repos"),
        "followers_count": user_data.get("followers"),
        "languages": list(set(filter(None, languages))),  # Unique languages
        "popular_repos": popular_repos,
    }

def download_pdf_from_ipfs(ipfs_url):
    """
    Download PDF from IPFS gateway and save to a temporary file
    """
    try:
        response = requests.get(ipfs_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        return temp_file_path
    except requests.RequestException as e:
        raise ValueError(f"Failed to download PDF from IPFS: {str(e)}")

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF resume, supporting both local and IPFS URLs
    """
    doc = None
    temp_file_path = None

    try:
        # Check if it's an IPFS URL
        if pdf_path.startswith('https://gateway.pinata.cloud/ipfs/'):
            temp_file_path = download_pdf_from_ipfs(pdf_path)
            pdf_path = temp_file_path
        
        # Open the document
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    finally:
        # Ensure the document is closed
        if doc:
            doc.close()
        
        # Safely attempt to remove temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except PermissionError:
                # Log this if you have logging set up
                print(f"Could not delete temporary file: {temp_file_path}")


def analyze_resume(resume_text):
    """
    Analyze resume content and extract key information like Skills, Experience, and Education.
    """
    # Extracting Skills section (assuming keywords like 'Skills' or 'Technologies' are used)
    skills_section = re.findall(r"(Skills|Technologies|Core Competencies|Skills:)(.*?)(Experience|Education|$)", resume_text, re.S)
    skills = []
    if skills_section:
        skills = skills_section[0][1].strip().split("\n")

    # Extracting Experience section (assuming 'Experience' or 'Work Experience' is a section title)
    experience_section = re.findall(r"(Experience|Work Experience|Professional Experience)(.*?)(Education|Skills|$)", resume_text, re.S)
    experience = []
    if experience_section:
        experience = experience_section[0][1].strip().split("\n")

    # Extracting Education section (assuming 'Education' is a section title)
    education_section = re.findall(r"(Education|Academic Background)(.*?)(Skills|Experience|$)", resume_text, re.S)
    education = []
    if education_section:
        education = education_section[0][1].strip().split("\n")

    return {
        "skills": skills,
        "experience": experience,
        "education": education,
    }

class UserSocialProfileAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, provider):
        user = request.user.profile

        if provider == 'github':
            if not user.github_url:
                return Response(
                    {'error': 'No GitHub URL found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                # Call the updated analyze_github function
                analytics = analyze_github(user.github_url)
                if 'error' in analytics:
                    return Response(
                        {'error': analytics['error']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                return Response(analytics, status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {'error': f'An unexpected error occurred: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        elif provider == 'resume':
            if not user.resume:
                return Response(
                    {'error': 'No resume found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            try:
                text = extract_text_from_pdf(user.resume)
                # Call the updated analyze_resume function
                analytics = analyze_resume(text)
                return Response(analytics, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'error': f'An unexpected error occurred: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            {'error': f'Unsupported provider: {provider}'},
            status=status.HTTP_400_BAD_REQUEST
        )
class UserJobMatcherView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.profile
        
        # Collect available social profiles
        available_profiles = {}
        
        # Check GitHub
        if user.github_url:
            try:
                github_analytics = analyze_github(user.github_url)
                available_profiles['github'] = github_analytics
            except Exception as e:
                # Log the error but continue processing
                print(f"GitHub analysis error: {str(e)}")
        
        
        # Check Resume
        if user.resume:
            try:
                text = extract_text_from_pdf(user.resume)
                resume_analytics = analyze_resume(text)
                available_profiles['resume'] = resume_analytics
            except Exception as e:
                print(f"Resume analysis error: {str(e)}")
        
        # If no profiles are available
        if not available_profiles:
            return Response(
                {'error': 'No social profiles found to analyze'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Use OpenAI to generate job recommendations
        try:
            client = OpenAI(base_url="https://YOUR-NODE-ID.us.gaianet.network/v1",api_key=os.getenv('OPENAI_API_KEY'))
            
            # Prepare profile data for OpenAI
            profile_summary = self._prepare_profile_summary(available_profiles)
            
            # Generate job recommendations
            job_recommendations = self._generate_job_recommendations(client, p+rofile_summary)
            
            # Save job matches
            saved_matches = self._save_job_matches(job_recommendations, user)
            
            return Response({
                'profile_analytics': available_profiles,
                'job_recommendations': saved_matches
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Job recommendation error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _prepare_profile_summary(self, profiles):
        """
        Consolidate profile information into a summary string
        """
        summary = ""
        
        if 'github' in profiles:
            summary += f"GitHub Profile: {profiles['github']}\n"
        
        
        if 'resume' in profiles:
            summary += f"Resume Summary: {profiles['resume']}\n"
        
        return summary
    
    def _generate_job_recommendations(self, openai_client, profile_summary):
        """
        Use OpenAI to generate job recommendations
        """
        response = openai_client.chat.completions.create(
            model="Meta-Llama-3-8B-Instruct-Q5_K_M",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a career advisor. Analyze the user's profile and suggest 1 most suitable job opportunities with a match score."
                },
                {
                    "role": "user", 
                    "content": f"Analyze this professional profile and recommend jobs:\n{profile_summary}"
                }
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        # Parse the job recommendations
        recommendations = json.loads(response.choices[0].message.content)
        return recommendations['jobs']
    
    def _save_job_matches(self, job_recommendations, user):
        """
        Save job matches using the JobMatchSerializer
        """
        job_matches = []
        for job in job_recommendations:
            serializer = JobMatchSerializer(data={
                'user_profile': user.id,
                'job_name': job['title'],
                'job_type': job.get('type', 'Unknown'),
                'job_description': job.get('description', ''),
                'company_name': job.get('company', ''),
                'location': job.get('location', ''),
                'job_url': job.get('url', ''),
                'match_score': job.get('match_score', 0)
            })
            
            if serializer.is_valid():
                job_match = serializer.save()
                job_matches.append(serializer.data)
        
        return job_matches