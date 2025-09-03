"""
Template manager for handling multiple resume templates
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manager for handling multiple resume templates"""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)

    def get_template(self, template_id: int, candidate_data: Dict[str, Any]) -> str:
        """
        Get HTML template for given template ID with candidate data populated

        Args:
            template_id: Template identifier (1, 2, etc.)
            candidate_data: Dictionary containing candidate information

        Returns:
            HTML string with populated template
        """
        if template_id == 1:
            return self._generate_template_1(candidate_data)
        elif template_id == 2:
            return self._generate_template_2(candidate_data)
        elif template_id == 3:
            return self._generate_template_3(candidate_data)
        else:
            raise ValueError(f"Template ID {template_id} not supported")

    def _generate_template_1(self, candidate_data: Dict[str, Any]) -> str:
        """Generate the original template (Template 1)"""
        # Generate links HTML
        links_html = ""
        for link in candidate_data.get("links", []):
            icon = "github" if "github" in link.lower() else "linkedin" if "linkedin" in link.lower() else "link"
            display_text = link.replace("https://", "").replace("http://", "").replace("www.", "")
            links_html += f"""
                        <div class="flex items-center gap-2 hover:text-blue-200 transition-colors">
                            <i data-lucide="{icon}" class="w-5 h-5"></i>
                            <span>{display_text}</span>
                        </div>"""

        # Generate experience HTML
        experience_html = ""
        for exp in candidate_data.get("experience", []):
            experience_html += f"""
                        <div data-gjs-type="experience" class="bg-gray-50 rounded-xl p-6 border-l-4 border-primary hover:shadow-lg transition-all duration-300">
                            <div data-gjs-type="no-selection" class="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4">
                                <div data-gjs-type="no-selection">
                                    <h3 data-gjs-type="no-selection"  class="experience-title text-xl font-semibold text-dark mb-1">{exp.get('title', '')}</h3>
                                    <p data-gjs-type="no-selection" class="experience-company text-primary font-medium text-lg">{exp.get('company', '')}</p>
                                </div>
                                <div data-gjs-type="no-selection" class="experience-dates bg-white px-4 py-2 rounded-lg text-sm font-medium text-gray-600 mt-2 lg:mt-0 inline-block">
                                    {exp.get('start_date', '')} - {exp.get('end_date', 'Present') if exp.get('end_date') else 'Present'}
                                </div>
                            </div>
                            <p data-gjs-type="no-selection" class="experience-description text-gray-700 leading-relaxed">{exp.get('description', '')}</p>
                        </div>"""

        # Generate education HTML
        education_html = ""
        for edu in candidate_data.get("education", []):
            education_html += f"""
                        <div data-gjs-type="education" class="bg-gradient-to-r from-secondary/5 to-primary/5 rounded-xl p-6 border border-gray-200">
                            <div data-gjs-type="no-selection" class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                                <div data-gjs-type="no-selection">
                                    <h3 data-gjs-type="no-selection" class="text-lg font-semibold text-dark mb-1">{edu.get('degree', '')}</h3>
                                    <p data-gjs-type="no-selection" class="text-secondary font-medium">{edu.get('institution', '')}</p>
                                </div>
                                <div data-gjs-type="no-selection" class="bg-white px-4 py-2 rounded-lg text-sm font-medium text-gray-600 mt-2 lg:mt-0 inline-block">
                                    {edu.get('start_date', '')} - {edu.get('end_date', 'Present') if edu.get('end_date') else 'Present'}
                                </div>
                            </div>
                        </div>"""

        # Generate skills tags
        def generate_skill_tags(skills, color):
            tags_html = ""
            for skill in skills:
                tags_html += f"""
                                <span class="inline-block bg-{color}-100 text-{color}-800 text-sm font-medium px-3 py-1 rounded-full border border-{color}-200 hover:bg-{color}-200 transition-colors">
                                    {skill}
                                </span>"""
            return tags_html

        programming_languages_tags = generate_skill_tags(
            candidate_data.get("technical_skills", {}).get("programming_languages", []), "blue"
        )
        frameworks_tags = generate_skill_tags(
            candidate_data.get("technical_skills", {}).get("frameworks", []), "purple"
        )
        skills_tags = generate_skill_tags(
            candidate_data.get("technical_skills", {}).get("skills", []), "green"
        )

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Resume Template</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'primary': '#3B82F6',
                        'secondary': '#1E40AF',
                        'accent': '#F59E0B',
                        'dark': '#1F2937',
                    }},
                    fontFamily: {{
                        'inter': ['Inter', 'system-ui', 'sans-serif'],
                    }}
                }}
            }}
        }}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
</head>
<body class="bg-gray-50 font-inter antialiased">
    <div class="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
        <div class="max-w-4xl mx-auto bg-white shadow-2xl rounded-xl overflow-hidden">
            <!-- Header Section -->
            <div class="bg-gradient-to-r from-primary to-secondary px-8 py-12 text-black relative overflow-hidden">
                <div class="absolute top-0 right-0 w-32 h-32 bg-white bg-opacity-10 rounded-full -mr-16 -mt-16"></div>
                <div class="absolute bottom-0 left-0 w-24 h-24 bg-white bg-opacity-10 rounded-full -ml-12 -mb-12"></div>
                <div class="relative z-10">
                    <h1 id="candidate-name" class="text-4xl lg:text-5xl font-bold mb-3 tracking-tight">
                        {candidate_data.get('name', 'Candidate Name')}
                    </h1>
                    <div class="flex flex-wrap items-center gap-6 text-lg">
                        <div class="flex items-center gap-2">
                            <i data-lucide="mail" class="w-5 h-5"></i>
                            <span id="candidate-email">{candidate_data.get('email', '')}</span>
                        </div>
                        <div id="candidate-links" class="flex flex-wrap gap-4">
                            {links_html}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="p-8">
                <!-- Key Accomplishments -->
                <section class="mb-12">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
                            <i data-lucide="star" class="w-5 h-5 text-white"></i>
                        </div>
                        <h2 class="text-2xl font-bold text-dark">Key Accomplishments</h2>
                    </div>
                    <div class="bg-gradient-to-r from-accent/5 to-primary/5 rounded-xl p-6 border-l-4 border-accent">
                        <p id="key-accomplishments" class="text-gray-700 leading-relaxed text-lg">
                            {candidate_data.get('key_accomplishments', '')}
                        </p>
                    </div>
                </section>

                <!-- Experience Section -->
                <section class="mb-12">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                            <i data-lucide="briefcase" class="w-5 h-5 text-white"></i>
                        </div>
                        <h2 class="text-2xl font-bold text-dark">Professional Experience</h2>
                    </div>
                    <div id="experience-list" class="space-y-6">
                        {experience_html}
                    </div>
                </section>

                <!-- Education Section -->
                <section class="mb-12">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 bg-secondary rounded-lg flex items-center justify-center">
                            <i data-lucide="graduation-cap" class="w-5 h-5 text-white"></i>
                        </div>
                        <h2 class="text-2xl font-bold text-dark">Education</h2>
                    </div>
                    <div id="education-list" class="space-y-4">
                        {education_html}
                    </div>
                </section>

                <!-- Technical Skills -->
                <section class="mb-8">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                            <i data-lucide="code" class="w-5 h-5 text-white"></i>
                        </div>
                        <h2 class="text-2xl font-bold text-dark">Technical Skills</h2>
                    </div>
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div id="programming-languages" class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
                            <h3 class="font-semibold text-lg text-blue-900 mb-4 flex items-center gap-2">
                                <i data-lucide="terminal" class="w-4 h-4"></i>
                                Programming Languages
                            </h3>
                            <div id="languages-tags" class="flex flex-wrap gap-2">
                                {programming_languages_tags}
                            </div>
                        </div>
                        <div id="frameworks" class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100">
                            <h3 class="font-semibold text-lg text-purple-900 mb-4 flex items-center gap-2">
                                <i data-lucide="layers" class="w-4 h-4"></i>
                                Frameworks & Tools
                            </h3>
                            <div id="frameworks-tags" class="flex flex-wrap gap-2">
                                {frameworks_tags}
                            </div>
                        </div>
                        <div id="skills" class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
                            <h3 class="font-semibold text-lg text-green-900 mb-4 flex items-center gap-2">
                                <i data-lucide="zap" class="w-4 h-4"></i>
                                Core Skills
                            </h3>
                            <div id="skills-tags" class="flex flex-wrap gap-2">
                                {skills_tags}
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </div>

    <script>
        // Initialize icons
        document.addEventListener('DOMContentLoaded', () => {{
            lucide.createIcons();
        }});
    </script>
</body>
</html>"""

        return html_template

    def _generate_template_2(self, candidate_data: Dict[str, Any]) -> str:
        """Generate the new Tailwind template (Template 2)"""
        # Extract candidate information with defaults
        name = candidate_data.get('name', 'Your Name')
        title = candidate_data.get('title', 'Full-Stack Web Developer')
        location = candidate_data.get('location', 'City, Country')
        email = candidate_data.get('email', 'you@example.com')
        phone = candidate_data.get('phone', '+00 0000 000000')
        portfolio_url = candidate_data.get('portfolio_url', '#')
        github_url = candidate_data.get('github_url', '#')
        summary = candidate_data.get('key_accomplishments', 'Concise statement of your value: the problems you solve, the tech you use, and the outcomes you deliver.')

        # Generate skills HTML
        skills_html = ""
        skills = candidate_data.get('technical_skills', {})
        all_skills = skills.get('programming_languages', []) + skills.get('frameworks', []) + skills.get('skills', [])
        if not all_skills:
            # Default skills if none provided
            all_skills = ['HTML5', 'CSS3', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'PostgreSQL', 'MongoDB', 'AWS', 'Linux']

        for skill in all_skills:
            skills_html += f'<li class="px-2 py-1 bg-slate-100 rounded-md">{skill}</li>'

        # Generate links HTML
        links_html = ""
        links = candidate_data.get('links', [])
        if links:
            for link in links:
                if 'github' in link.lower():
                    links_html += f'''
                    <li>
                      <a class="inline-flex items-center gap-2 group" href="{link}">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4 opacity-70 group-hover:opacity-100"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12a9.997 9.997 0 0 0 6.837 9.488c.5.092.683-.217.683-.483 0-.237-.009-.866-.014-1.7-2.782.604-3.369-1.34-3.369-1.34-.455-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.607.069-.607 1.004.07 1.532 1.031 1.532 1.031.892 1.528 2.341 1.087 2.91.832.091-.647.35-1.087.636-1.338-2.22-.252-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.03-2.683-.103-.253-.447-1.271.098-2.65 0 0 .84-.269 2.75 1.025a9.564 9.564 0 0 1 2.5-.336 9.56 9.56 0 0 1 2.5.336c1.91-1.294 2.75-1.025 2.75-1.025.545 1.379.201 2.397.098 2.65.64.699 1.03 1.592 1.03 2.683 0 3.842-2.338 4.688-4.566 4.936.359.31.679.92.679 1.852 0 1.337-.012 2.417-.012 2.747 0 .268.18.58.688.481A10.001 10.001 0 0 0 22 12c0-5.523-4.477-10-10-10Z" clip-rule="evenodd"/></svg>
                        <span class="underline decoration-slate-300">GitHub</span>
                      </a>
                    </li>'''
                elif 'portfolio' in link.lower() or 'website' in link.lower():
                    links_html += f'''
                    <li>
                      <a class="inline-flex items-center gap-2 group" href="{link}">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4 opacity-70 group-hover:opacity-100"><path d="M14 3a1 1 0 0 1 1 1v3h-2V5H6v14h7v-2h2v3a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h9Zm3.293 6.293 1.414 1.414L15.414 14l3.293 3.293-1.414 1.414L12.586 14l4.707-4.707Z"/></svg>
                        <span class="underline decoration-slate-300">Portfolio</span>
                      </a>
                    </li>'''
        else:
            # Default links if none provided
            links_html = '''
                    <li>
                      <a class="inline-flex items-center gap-2 group" href="#">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4 opacity-70 group-hover:opacity-100"><path d="M14 3a1 1 0 0 1 1 1v3h-2V5H6v14h7v-2h2v3a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h9Zm3.293 6.293 1.414 1.414L15.414 14l3.293 3.293-1.414 1.414L12.586 14l4.707-4.707Z"/></svg>
                        <span class="underline decoration-slate-300">Portfolio</span>
                      </a>
                    </li>
                    <li>
                      <a class="inline-flex items-center gap-2 group" href="#">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4 opacity-70 group-hover:opacity-100"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12a9.997 9.997 0 0 0 6.837 9.488c.5.092.683-.217.683-.483 0-.237-.009-.866-.014-1.7-2.782.604-3.369-1.34-3.369-1.34-.455-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.607.069-.607 1.004.07 1.532 1.031 1.532 1.031.892 1.528 2.341 1.087 2.91.832.091-.647.35-1.087.636-1.338-2.22-.252-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.03-2.683-.103-.253-.447-1.271.098-2.65 0 0 .84-.269 2.75 1.025a9.564 9.564 0 0 1 2.5-.336 9.56 9.56 0 0 1 2.5.336c1.91-1.294 2.75-1.025 2.75-1.025.545 1.379.201 2.397.098 2.65.64.699 1.03 1.592 1.03 2.683 0 3.842-2.338 4.688-4.566 4.936.359.31.679.92.679 1.852 0 1.337-.012 2.417-.012 2.747 0 .268.18.58.688.481A10.001 10.001 0 0 0 22 12c0-5.523-4.477-10-10-10Z" clip-rule="evenodd"/></svg>
                        <span class="underline decoration-slate-300">GitHub</span>
                      </a>
                    </li>
                    <li>
                      <a class="inline-flex items-center gap-2 group" href="mailto:{email}">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4 opacity-70 group-hover:opacity-100"><path d="M2 6.5A2.5 2.5 0 0 1 4.5 4h15A2.5 2.5 0 0 1 22 6.5v11A2.5 2.5 0 0 1 19.5 20h-15A2.5 2.5 0 0 1 2 17.5v-11Zm2.5-.5a.5.5 0 0 0-.5.5v.217l8 4.8 8-4.8V6.5a.5.5 0 0 0-.5-.5h-15Zm15 12a.5.5 0 0 0 .5-.5V9.63l-7.6 4.56a1 1 0 0 1-1.02 0L4 9.63V17.5a.5.5 0 0 0 .5.5h15Z"/></svg>
                        <span class="underline decoration-slate-300">{email}</span>
                      </a>
                    </li>
                    <li class="flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4 opacity-70"><path fill-rule="evenodd" d="M1.5 4.5A3 3 0 0 1 4.5 1.5h15a3 3 0 0 1 3 3v15a3 3 0 0 1-3 3h-15a3 3 0 0 1-3-3v-15Zm6.75 2.25a.75.75 0 0 0-1.5 0v10.5a.75.75 0 0 0 1.5 0V6.75ZM18 9a.75.75 0 0 0-1.5 0v6a.75.75 0 0 0 1.5 0V9Z" clip-rule="evenodd"/></svg>
                      <span>{phone}</span>
                    </li>'''

        # Generate experience HTML
        experience_html = ""
        experiences = candidate_data.get('experience', [])
        if not experiences:
            # Default experiences if none provided
            experiences = [
                {
                    'title': 'Full-Stack Web Developer',
                    'company': 'Freelance',
                    'dates': 'Jun 2018 – Present',
                    'description': 'Build full-stack web apps end-to-end with React/Node, from idea to deployment. Design data models and implement REST/GraphQL APIs with PostgreSQL/MongoDB. Improve performance, accessibility, and reliability across modern browsers.'
                },
                {
                    'title': 'Computer Repair Technician',
                    'company': 'Freelance',
                    'dates': 'Mar 2018 – Present',
                    'description': 'Diagnose and resolve hardware/software issues across Windows, macOS, and Linux. Deliver upgrades, malware removal, and data protection with clear client hand-offs.'
                },
                {
                    'title': 'Assistant Manager — Retail',
                    'company': '',
                    'dates': 'May 2012 – Apr 2018',
                    'description': 'Led training on product knowledge, engagement, and sales for a high-traffic store. Maintained operations and merchandising standards to maximize customer satisfaction.'
                }
            ]

        for exp in experiences:
            experience_html += f'''
                <article data-gjs-type="experience">
                  <div data-gjs-type="no-selection" class="flex flex-col md:flex-row md:items-baseline md:justify-between gap-1">
                    <h3 data-gjs-type="no-selection" class="experience-title font-semibold text-lg">{exp.get('title', '')} -<span class="experience-company">{exp.get('company', '')}</span></h3>
                    <p data-gjs-type="no-selection" class="experience-dates text-sm text-slate-500">{exp.get('dates', '')}</p>
                  </div>
                  <ul data-gjs-type="no-selection" class="mt-2 list-disc list-outside space-y-1 pl-5 text-[15px] leading-relaxed">
                    <li data-gjs-type="no-selection expe-description">{exp.get('description', '')}</li>
                  </ul>
                </article>'''

        # Generate education HTML
        education_html = ""
        educations = candidate_data.get('education', [])
        if not educations:
            # Default education if none provided
            educations = [
                {
                    'degree': 'Bachelor of Science',
                    'institution': 'University Name',
                    'dates': '2019 – 2023',
                    'gpa': 'GPA: 3.9'
                },
                {
                    'degree': 'Certificate / Bootcamp',
                    'institution': '',
                    'dates': 'Year · Subject',
                    'gpa': 'Topics: HTML, CSS, JavaScript, Web Development'
                }
            ]

        for edu in educations:
            education_html += f'''
                <article data-gjs-type="education">
                  <div data-gjs-type="no-selection" class="flex flex-col md:flex-row md:items-baseline md:justify-between gap-1">
                    <h3 data-gjs-type="no-selection" class="font-semibold">{edu.get('degree', '')}</h3>
                    <p data-gjs-type="no-selection" class="text-sm text-slate-500">{edu.get('dates', '')}</p>
                  </div>
                  <p data-gjs-type="no-selection" class="text-[15px] text-slate-700 mt-1">{edu.get('gpa', '')}</p>
                </article>'''

        # Generate projects HTML
        projects_html = ""
        projects = candidate_data.get('projects', [])
        if not projects:
            # Default project if none provided
            projects = [
                {
                    'name': 'Project Name',
                    'tech': 'Tech · Link',
                    'description': 'One-line description of the problem, your approach, and the measurable outcome.'
                }
            ]

        for project in projects:
            projects_html += f'''
                <article>
                  <div class="flex flex-col md:flex-row md:items-baseline md:justify-between gap-1">
                    <h3 class="font-semibold">{project.get('name', '')}</h3>
                    <p class="text-sm text-slate-500">{project.get('tech', '')}</p>
                  </div>
                  <p class="text-[15px] text-slate-700 mt-1">{project.get('description', '')}</p>
                </article>'''

        html_template = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Resume – Tailwind CSS</title>
    <!-- Tailwind CDN for a single-file demo. For production, compile a custom build. -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      /* Print/A4 friendly */
      @page {{ size: A4; margin: 12mm; }}
      @media print {{
        html, body {{ background: #fff !important; }}
      }}
    </style>
  </head>
  <body class="bg-slate-100 text-slate-800 antialiased print:bg-white">
    <main class="mx-auto max-w-4xl md:my-10 md:p-0 p-0">
      <section class="bg-white shadow-lg rounded-2xl md:p-10 p-6 print:shadow-none print:rounded-none">
        <!-- Header -->
        <header class="border-b border-slate-200 pb-6 md:pb-8">
          <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 class="text-3xl md:text-4xl font-bold tracking-tight">{name}</h1>
              <p class="text-slate-600 mt-1 text-lg">{title}</p>
              <p class="text-slate-500 text-sm">{location}</p>
            </div>
            <div class="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-slate-600">
              <a class="hover:text-slate-900 underline decoration-slate-300" href="{portfolio_url}" aria-label="Portfolio link">Portfolio</a>
              <a class="hover:text-slate-900 underline decoration-slate-300" href="{github_url}" aria-label="GitHub profile">GitHub</a>
              <a class="hover:text-slate-900 underline decoration-slate-300" href="mailto:{email}" aria-label="Email">{email}</a>
              <span aria-label="Phone">{phone}</span>
            </div>
          </div>
        </header>

        <!-- Body -->
        <div class="grid md:grid-cols-3 gap-8 pt-6 md:pt-8">
          <!-- Sidebar / Left column -->
          <aside class="md:col-span-1 space-y-8">
            <!-- Summary (compact) -->
            <section>
              <h2 class="text-sm font-semibold tracking-wider text-slate-500">SUMMARY</h2>
              <p class="mt-2 text-sm leading-relaxed text-slate-700">
                {summary}
              </p>
            </section>

            <!-- Skills -->
            <section>
              <h2 class="text-sm font-semibold tracking-wider text-slate-500">SKILLS</h2>
              <ul class="mt-3 grid grid-cols-2 gap-2 text-sm">
                {skills_html}
              </ul>
            </section>

            <!-- Links -->
            <section>
              <h2 class="text-sm font-semibold tracking-wider text-slate-500">LINKS</h2>
              <ul class="mt-3 space-y-2 text-sm">
                {links_html}
              </ul>
            </section>
          </aside>

          <!-- Main column -->
          <section class="md:col-span-2 space-y-10">
            <!-- Summary (expanded) -->
            <section class="hidden md:block">
              <h2 class="text-sm font-semibold tracking-wider text-slate-500">SUMMARY</h2>
              <p class="mt-2 text-[15px] leading-relaxed text-slate-700">
                {summary}
              </p>
            </section>

            <!-- Experience -->
            <section>
              <h2 class="text-sm font-semibold tracking-wider text-slate-500">EXPERIENCE</h2>
              <div class="mt-4 space-y-6">
                {experience_html}
              </div>
            </section>

            <!-- Education -->
            <section>
              <h2 class="text-sm font-semibold tracking-wider text-slate-500">EDUCATION</h2>
              <div class="mt-4 space-y-5">
                {education_html}
              </div>
            </section>

            <!-- Optional: Projects -->
            <section>
              <h2 class="text-sm font-semibold tracking-wider text-slate-500">PROJECTS</h2>
              <div class="mt-4 space-y-4">
                {projects_html}
              </div>
            </section>
          </section>
        </div>

        <!-- Footer / Actions -->
        <div class="mt-8 flex items-center justify-between print:hidden">
          <p class="text-xs text-slate-500">Single-file Tailwind resume template. Customize and print to PDF.</p>
          <button onclick="window.print()" class="px-4 py-2 rounded-lg border border-slate-300 hover:border-slate-400 text-sm">Print / Save PDF</button>
        </div>
      </section>
    </main>
  </body>
</html>'''

        return html_template

    def _generate_template_3(self, candidate_data: Dict[str, Any]) -> str:
        """Generate the modern CV template (Template 3) with sidebar and skill meters"""
        # Extract candidate information with defaults
        name = candidate_data.get('name', 'YOUR NAME')
        title = candidate_data.get('title', 'Full-Stack Developer')
        email = candidate_data.get('email', 'you@example.com')
        phone = candidate_data.get('phone', '+00 0000 000000')
        location = candidate_data.get('location', 'City, Country')
        portfolio_url = candidate_data.get('portfolio_url', '#')
        summary = candidate_data.get('key_accomplishments', 'Brief professional summary highlighting your years of experience, domain strengths, and the outcomes you deliver. Keep it concise and impact-focused.')

        # Generate contact links
        contact_links = candidate_data.get('links', [])
        portfolio_link = portfolio_url
        if contact_links:
            for link in contact_links:
                if 'portfolio' in link.lower() or 'website' in link.lower():
                    portfolio_link = link
                    break

        # Generate skills with proficiency levels
        skills_html = ""
        skills_data = candidate_data.get('technical_skills', {})
        all_skills = []

        # Combine all skill types
        for skill in skills_data.get('programming_languages', []):
            all_skills.append({'name': skill, 'level': 'Expert', 'dots': 8})
        for skill in skills_data.get('frameworks', []):
            all_skills.append({'name': skill, 'level': 'Advanced', 'dots': 7})
        for skill in skills_data.get('skills', []):
            all_skills.append({'name': skill, 'level': 'Intermediate', 'dots': 6})

        # Default skills if none provided
        if not all_skills:
            all_skills = [
                {'name': 'React', 'level': 'Expert', 'dots': 8},
                {'name': 'Node.js', 'level': 'Advanced', 'dots': 7},
                {'name': 'TypeScript', 'level': 'Advanced', 'dots': 6}
            ]

        # Generate skills HTML with dot meters
        for skill in all_skills[:5]:  # Limit to 5 skills for space
            filled_dots = skill['dots']
            empty_dots = 10 - filled_dots
            dots_html = ""

            # Filled dots
            for _ in range(filled_dots):
                dots_html += '<span class="w-2 h-2 rounded-full bg-sky-500"></span>'

            # Empty dots
            for _ in range(empty_dots):
                dots_html += '<span class="w-2 h-2 rounded-full bg-slate-300"></span>'

            skills_html += f'''
                <li>
                  <div class="flex items-center justify-between text-sm">
                    <span>{skill['name']}</span>
                    <span class="text-xs text-slate-500">{skill['level']}</span>
                  </div>
                  <div class="mt-2 flex gap-1">
                    {dots_html}
                  </div>
                </li>'''

        # Generate languages (default if not provided)
        languages = candidate_data.get('languages', [])
        if not languages:
            languages = [
                {'name': 'English', 'level': 'Fluent'},
                {'name': 'Tamil', 'level': 'Native'}
            ]

        languages_html = ""
        for lang in languages:
            languages_html += f'''
                <li class="flex items-center justify-between">
                  <span>{lang['name']}</span>
                  <span class="text-xs text-slate-500">{lang['level']}</span>
                </li>'''

        # Generate experience HTML
        experience_html = ""
        experiences = candidate_data.get('experience', [])
        if not experiences:
            # Default experiences if none provided
            experiences = [
                {
                    'title': 'Senior Software Engineer · Company Name',
                    'dates': '2022 – Present',
                    'description': [
                        'Designed and built scalable web apps with React, Node.js, and PostgreSQL.',
                        'Improved performance and accessibility; reduced page load by 40%.',
                        'Mentored juniors and led code reviews to raise code quality.'
                    ]
                },
                {
                    'title': 'Full-Stack Developer · Company Name',
                    'dates': '2020 – 2022',
                    'description': [
                        'Delivered features end-to-end: UI, API, data models, CI/CD.',
                        'Collaborated with designers to polish UX and micro-interactions.'
                    ]
                }
            ]

        for exp in experiences:
            bullets = ""
            desc_list = exp.get('description', [])
            if isinstance(desc_list, str):
                desc_list = [desc_list]

            for desc in desc_list:
                bullets += f'<li data-gjs-type="no-selection">{desc}</li>'

            experience_html += f'''
                <article data-gjs-type="experience">
                  <div data-gjs-type="no-selection" class="flex flex-col md:flex-row md:items-baseline md:justify-between gap-1">
                    <h3 data-gjs-type="no-selection" class="experience-title font-semibold text-lg">{exp.get('title', '')} -<span class="experience-company">{exp.get('company', '')}</span></h3>
                    <p data-gjs-type="no-selection" class="experience-dates text-sm text-sky-600">{exp.get('dates', '')}</p>
                  </div>
                  <ul data-gjs-type="no-selection" class="experience-description mt-2 list-disc list-outside space-y-1 pl-5 text-[15px] leading-relaxed">
                    {bullets}
                  </ul>
                </article>'''

        # Generate education HTML
        education_html = ""
        educations = candidate_data.get('education', [])
        if not educations:
            # Default education if none provided
            educations = [
                {
                    'degree': 'BSc (Hons) in Software Engineering',
                    'institution': 'University Name',
                    'dates': '2018 – 2021'
                },
                {
                    'degree': 'Certificate / Bootcamp',
                    'institution': 'Provider Name',
                    'dates': 'Year'
                }
            ]

        for edu in educations:
            education_html += f'''
                <article data-gjs-type="education" class="flex items-baseline justify-between gap-4">
                  <div data-gjs-type="no-selection">
                    <h3 data-gjs-type="no-selection" class="font-semibold">{edu.get('degree', '')}</h3>
                    <p data-gjs-type="no-selection" class="text-[15px] text-slate-700">{edu.get('institution', '')}</p>
                  </div>
                  <p data-gjs-type="no-selection" class="text-sm text-sky-600">{edu.get('dates', '')}</p>
                </article>'''

        html_template = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Modern CV – Tailwind</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      @page {{ size: A4; margin: 12mm; }}
      @media print {{ html, body {{ background: #fff !important; }} }}
    </style>
  </head>
  <body class="bg-slate-100 text-slate-800 antialiased">
    <main class="mx-auto max-w-4xl md:my-10 p-0">
      <section class="bg-white shadow-lg rounded-2xl overflow-hidden print:shadow-none print:rounded-none">
        <!-- Top band (accent) -->
        <div class="h-2 w-full bg-sky-500"></div>

        <div class="grid grid-cols-12 gap-0">
          <!-- Sidebar -->
          <aside class="col-span-12 md:col-span-4 bg-slate-50 md:border-r border-slate-200 p-8">
            <!-- Photo -->
            <div class="w-40 h-40 mx-auto rounded-full overflow-hidden ring-4 ring-white shadow mb-6">
              <img src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=600&auto=format&fit=crop" alt="Profile photo" class="w-full h-full object-cover" />
            </div>

            <!-- Contact -->
            <section class="space-y-2">
              <h2 class="text-xs tracking-[0.2em] font-semibold text-slate-500">CONTACT</h2>
              <ul class="mt-3 space-y-2 text-sm">
                <li class="flex gap-3"><span class="i">📞</span><span>{phone}</span></li>
                <li class="flex gap-3"><span class="i">✉️</span><a class="underline decoration-slate-300" href="mailto:{email}">{email}</a></li>
                <li class="flex gap-3"><span class="i">🌐</span><a class="underline decoration-slate-300" href="{portfolio_link}">portfolio.example</a></li>
                <li class="flex gap-3"><span class="i">📍</span><span>{location}</span></li>
              </ul>
            </section>

            <!-- Divider -->
            <div class="my-6 h-px bg-slate-200"></div>

            <!-- Skills (dot meter) -->
            <section>
              <h2 class="text-xs tracking-[0.2em] font-semibold text-slate-500">SKILLS</h2>
              <ul class="mt-3 space-y-3">
                {skills_html}
              </ul>
            </section>

            <!-- Divider -->
            <div class="my-6 h-px bg-slate-200"></div>

            <!-- Languages -->
            <section>
              <h2 class="text-xs tracking-[0.2em] font-semibold text-slate-500">LANGUAGES</h2>
              <ul class="mt-3 space-y-2 text-sm">
                {languages_html}
              </ul>
            </section>
          </aside>

          <!-- Main -->
          <section class="col-span-12 md:col-span-8 p-8 md:p-10">
            <!-- Name & Title -->
            <header class="border-b border-slate-200 pb-6">
              <h1 class="text-3xl md:text-4xl font-bold tracking-tight">{name}</h1>
              <p class="text-slate-600 mt-1 text-lg">{title}</p>
            </header>

            <!-- Profile / Summary -->
            <section class="mt-6">
              <h2 class="text-xs tracking-[0.2em] font-semibold text-slate-500">PROFILE</h2>
              <p class="mt-3 text-[15px] leading-relaxed text-slate-700">
                {summary}
              </p>
            </section>

            <!-- Experience -->
            <section class="mt-8">
              <h2 class="text-xs tracking-[0.2em] font-semibold text-slate-500">EXPERIENCE</h2>
              <div class="mt-4 space-y-6">
                {experience_html}
              </div>
            </section>

            <!-- Education -->
            <section class="mt-8">
              <h2 class="text-xs tracking-[0.2em] font-semibold text-slate-500">EDUCATION</h2>
              <div class="mt-4 space-y-5">
                {education_html}
              </div>
            </section>

            <!-- References / Extras -->
            <section class="mt-8">
              <h2 class="text-xs tracking-[0.2em] font-semibold text-slate-500">REFERENCES</h2>
              <p class="mt-3 text-[15px] text-slate-700">Available upon request.</p>
            </section>

            <!-- Footer actions -->
            <div class="mt-10 flex justify-end print:hidden">
              <button onclick="window.print()" class="px-4 py-2 rounded-lg border border-slate-300 hover:border-slate-400 text-sm">Print / Save PDF</button>
            </div>
          </section>
        </div>
      </section>
    </main>
  </body>
</html>'''

        return html_template

    def get_available_templates(self) -> Dict[int, str]:
        """Get list of available template IDs and their descriptions"""
        return {
            1: "Modern gradient template with icons and cards",
            2: "Clean Tailwind template optimized for print/PDF",
            3: "Modern CV template with sidebar, photo, and skill meters"
        }


# Global template manager instance
template_manager = TemplateManager()


def get_template_manager() -> TemplateManager:
    """Dependency injection for template manager"""
    return template_manager
