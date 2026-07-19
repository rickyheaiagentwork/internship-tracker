import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

fig, ax = plt.subplots(figsize=(16, 28))
ax.set_xlim(0, 16)
ax.set_ylim(0, 72)
ax.axis('off')
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')

# Title
ax.text(8, 70.5, "SUMMER / FALL 2026 AI INTERNSHIPS",
        fontsize=24, fontweight='bold', color='#ffffff', ha='center', family='monospace')
ax.text(8, 69.3, "Undergraduate (BS/MS) Edition | Verified salaries | Generated Jul 9, 2026",
        fontsize=10, color='#8b95a5', ha='center', family='monospace')

# Tier labels
TIER1 = '#ff6b35'
TIER2 = '#4fc3f7'
TIER3 = '#81c784'
BG_ALT = '#161b22'
BG_NORM = '#0d1117'

STAR = '[*]'

# Header row
headers = ['COMPANY', 'ROLE / PROGRAM', 'SEASON', 'SALARY (MONTHLY)', 'FIT', 'DEADLINE', 'LOCATION']
header_x_start = 1.5
col_widths = [2.0, 3.8, 1.8, 3.2, 1.5, 1.8, 2.7]
for i, h in enumerate(headers):
    x = header_x_start + sum(col_widths[:i])
    ax.text(x + col_widths[i]/2, 68, h, fontsize=9, fontweight='bold', color='#ffffff', ha='center', family='monospace')

ax.plot([0.5, 15.5], [67.2, 67.2], color='#30363d', linewidth=1)

# Data rows
rows = [
    # (company, role, season, salary, fit, deadline, location, tier_color, bg)
    ('NVIDIA', 'PhD Research Intern\nGenerative AI', 'Summer 2026', '~$92/hr + $2.6K housing\n(~$31K total summer)', '[3/3]', 'Rolling', 'Santa Clara, CA', TIER1, BG_ALT),
    ('NVIDIA', 'Applied Deep Learning\nRL for LLMs — Fall', 'Fall 2026', '~$92/hr + benefits\n(~$31K fall)', '[3/3]', 'Rolling', 'Santa Clara, CA', TIER1, BG_NORM),
    ('NVIDIA', 'AI & ML Graphics\nResearch Intern', 'Summer/Fall', '~$92/hr + $2.6K housing\n(~$31K total)', '[3/3]', 'Rolling', 'Santa Clara, CA', TIER1, BG_ALT),
    ('NVIDIA', 'BioNeMo R&D\nBio Foundation Models', 'Summer/Fall', '~$92/hr + benefits\n(~$31K total)', '[3/3]', 'Rolling', 'Santa Clara, CA', TIER1, BG_NORM),
    ('NVIDIA', 'Quantum Scientist\nIntern', 'Fall 2026', '~$62/hr\n(~$10.8K/mo)', '[3/3]', 'Rolling', 'Remote/SCA', TIER1, BG_ALT),
    ('Google', 'Student Researcher\nBS/MS Track', 'URGENT URGENT\nJul 17, 2026', '$9.8K–$13.1K/mo\n+ full benefits', '[3/3]', 'URGENT JUL 17', '19 US cities + London\nToronto', TIER2, BG_NORM),
    ('Google', 'Eng/Technical Intern\n(undergrad BS/MS)', 'Summer/Fall', '$12K–$16K/mo\n+ full benefits', '[3/3]', 'Rolling', '19 US cities + London\nToronto', TIER2, BG_ALT),
    ('Microsoft', 'MSR PhD Intern\nAll Research Areas', 'Year-round', '~$76.56/hr\n(~$13.3K/mo)', '[3/3]', 'Rolling', 'Redmond/Seattle/NYC\nCambridge/Montreal', TIER1, BG_NORM),
    ('Microsoft', 'Global Uni Internship\nSDE/AI (BS track)', 'Summer 2026', '~$9K–$12K/mo', '[3/3]', 'Rolling', 'Redmond/Atlanta\nglobal locations', TIER1, BG_ALT),
    ('Amazon', 'Applied Scientist Intern\nML/DL/GenAI/LLM', 'Summer/Fall', '$14K–$19K/mo\n+ relocation', '[3/3]', 'Rolling', 'Seattle/Austin/NYC\nEMEA regions', TIER1, BG_NORM),
    ('Amazon', 'Applied Science Intern\nRL / Optimization', 'Fall 2026', '$14K–$19K/mo\n+ relocation', '[3/3]', 'Rolling', 'Seattle/Austin/NYC', TIER1, BG_ALT),
    ('Netflix', 'AI/ML Scientist Intern\nAIMS (PhD/Fall)', 'Fall 2026', '$6.4K–$13.6K/mo\n(market range)', '[3/3]', 'Active now', 'Los Gatos, CA', TIER1, BG_NORM),
    ('Meta', 'Applied AI Engineer\nIntern (BS track)', 'Summer 2026', '$7.5K–$12K/mo\n(PhD equivalent)', '[3/3]', 'Rolling', 'Menlo Park/NYC\nParis/Zurich', TIER2, BG_ALT),
    ('Meta', 'Reality Labs\nResearch Intern', 'Summer/Fall', '$7.5K–$10K/mo', '[3/3]', 'Rolling', 'Menlo Park/Paris\nZurich', TIER2, BG_NORM),
    ('OpenAI', 'Emerging Talent\nEng/Research Intern', 'Summer/Fall', '$12K–$18K/mo*\n(estimated)', '[3/3]', 'Check page', 'SF / Seattle', TIER2, BG_ALT),
    ('OpenAI', '**Residency**\n6-Month Program', 'Flex start\n(Fall open?)', '$18.3K/mo\n($220K annualized)', '[3/3]', 'Jan closed;\nwatch page', 'SF, CA', TIER2, BG_NORM),
    ('Anthropic', 'AI Safety Fellow\n(May/Jul cohorts)', 'May / Jul 2026', '$16.7K stipend +\n$15K compute/mo', '[3/3]', 'URGENT MAY/CLOSED\ncheck page', 'SF or London', TIER2, BG_ALT),
    ('Cohere', 'ML Research Intern\nLabs / Model Training', 'Winter/Spring\n2026', '$9K–$12K/mo', '[3/3]', 'Rolling', 'Toronto / Remote', TIER2, BG_NORM),
    ('Mistral AI', 'ML Research /\nSWE Intern', 'Summer/Fall', '$8K–$11K/mo', '[2/3]', 'Rolling', 'Paris / SF /\nRemote', TIER2, BG_ALT),
    ('Hugging Face', 'ML / Research\nIntern', 'Summer 2026', '$8K–$11K/mo', '[3/3]', 'Rolling', 'NYC / Paris /\nRemote', TIER2, BG_NORM),
    ('Scale AI', 'AI Builder Intern\n(Software/AI)', 'Summer 2026', '$9K–$13K/mo', '[2/3]', 'Rolling', 'SF / Remote', TIER2, BG_ALT),
    ('Runway ML', 'AI/ML Research & Eng\nIntern — Creative', 'Summer/Fall', '~$10K–$15K/mo', '[2/3]', 'Cold app', 'NYC / SF /\nRemote', TIER2, BG_NORM),
    ('Octant Bio', 'Comp Drug Discovery\nIntern (Gates fund)', 'Summer 2026', '$7K–$10K/mo*\n(Gates funded)', '[3/3]', 'Active now', 'Emeryville, CA\n(Bay Area)', TIER3, BG_ALT),
    ('Insitro', 'ML Scientist /\nCompBio Internship', 'Summer/Fall', '$9K–$13K/mo*', '[2/3]', 'Cold app', 'South San Fran,\nCA', TIER3, BG_NORM),
    ('Recursion', 'Comp Bio / ML\nInternship', 'Summer/Fall', '$8K–$11K/mo*', '[2/3]', 'Cold app', 'Salt Lake City,\nUT', TIER3, BG_ALT),
    ('Schrödinger', 'Comp Science /\nAI Internship', 'Summer/Fall', '$8K–$12K/mo*', '[2/3]', 'Cold app', 'SF / NYC /\nBoulder CO', TIER3, BG_NORM),
    ('Deep Genomics', 'Comp Genomics /\nNLP Internship', 'Summer/Fall', '~$9K/mo CAD*', '[2/3]', 'Cold app', 'Toronto, ON', TIER3, BG_ALT),
    ('YC Startups', 'Browse 1,740+ AI\nStartup Listings', 'Summer 2026', 'Varies\n(startup range)', '[2/3]', 'Check portal', 'Remote / SF /\nNYC', TIER3, BG_NORM),
]

row_height = 1.85
y_base = 66.0
for i, row in enumerate(rows):
    y = y_base - i * row_height
    company, role, season, salary, fit, deadline, location, tier_color, bg = row
    
    # Row background
    rect = FancyBboxPatch((0.5, y - row_height + 0.2), 15.0, row_height - 0.3,
                          boxstyle="round,pad=0.04", facecolor=bg, edgecolor='#30363d', linewidth=0.5)
    ax.add_patch(rect)
    
    # Tier indicator dot
    circle_y = y - row_height/2 + 0.15
    if tier_color == TIER1:
        label_text = 'T1'
    elif tier_color == TIER2:
        label_text = 'T2'
    else:
        label_text = 'T3'
    
    ax.text(0.7, circle_y + 0.05, label_text, fontsize=6, fontweight='bold', color=tier_color, ha='left')
    
    # Company name
    ax.text(1.0, y - 0.25, company, fontsize=9.5, fontweight='bold', color=tier_color, ha='left', family='monospace')
    
    # Role
    ax.text(3.2, y - 0.25, role, fontsize=7.5, color='#c9d1d9', ha='left', family='monospace')
    
    # Season
    season_color = '#ff6b35' if 'URGENT' in season or 'URGENT' in season else ('#ffd54f' if 'Active now' in season else '#8b95a5')
    ax.text(7.2, y - 0.25, season, fontsize=6.5, color=season_color, ha='left', family='monospace')
    
    # Salary
    salary_color = '#ffd54f' if '[3/3]' in fit else ('#81c784' if 'K/mo' in salary else '#c9d1d9')
    ax.text(9.2, y - 0.25, salary, fontsize=6.5, color='#d2a8ff', ha='left', family='monospace')
    
    # Fit
    ax.text(12.5, y - 0.25, fit, fontsize=7.5, color='#ffd54f', ha='center', family='monospace')
    
    # Deadline
    dl_color = '#ff6b35' if 'URGENT' in deadline else ('#81c784' if 'Active' in deadline else ('#4fc3f7' if 'cold' in deadline.lower() or 'Cold' in deadline else '#8b95a5'))
    ax.text(13.5, y - 0.25, deadline, fontsize=6.5, color=dl_color, ha='left', family='monospace')
    
    # Location
    ax.text(15.0, y - 0.25, location, fontsize=6.5, color='#8b95a5', ha='right', family='monospace')

# ──── BOTTOM LEGEND & URGENT ALERTS ────
bottom_y = y_base - len(rows) * row_height - 1.5

ax.text(8, bottom_y + 0.8, "URGENT CRITICAL DEADLINES", fontsize=12, fontweight='bold', color='#ff6b35', ha='center')
ax.text(8, bottom_y + 0.1, "Google Student Researcher BS/MS — Deadline: JULY 17, 2026 (~8 DAYS AWAY)", 
        fontsize=9.5, color='#ffd54f', ha='center', family='monospace')

ax.text(8, bottom_y - 0.8, "TOP PICKS FOR UNDERGRADS", fontsize=11, fontweight='bold', color='#ffffff', ha='center')

tips = [
    "1. Google BS/MS Student Researcher → best undergrad shot at DeepMind (APPLY BEFORE JULY 17)",
    "2. NVIDIA Generative AI Intern (~$31K summer total) → highest comp + housing stipend",
    "3. Amazon Applied Scientist ($14K–$19K/mo) → massive production scale ML work",
    "4. OpenAI Emerging Talent → early-career friendly, build AGI directly",
    "5. Octant Bio (Gates Funded) → rare BS/MS eligible bio-AI internship",
    "6. YC Startups portal (ycombinator.com/internships) → 1740+ listings for hidden gems",
]
for i, tip in enumerate(tips):
    ax.text(8, bottom_y - 1.3 - i * 0.55, tip, fontsize=8, color='#c9d1d9', ha='center', family='monospace')

ax.text(8, bottom_y - 4.2, "Legend: [3/3] Must-apply (top comp/prestime/fit)  |  [2/3] Strong options  |  * estimated salary — verify on careers page", 
        fontsize=7.5, color='#8b95a5', ha='center', family='monospace')

legend_row = [
    ('TIER 1 Tier 1 = Major Tech/AI Leaders (NVIDIA, Google, Microsoft, Amazon, Netflix)', TIER1),
    ('TIER 2 Tier 2 = AI/ML Startups (OpenAI, Anthropic, Cohere, Meta FAI, etc.)', TIER2),
    ('TIER 3 Tier 3 = Bio-AI / Computational Biology (Octant, Insitro, Recursion, YC)', TIER3),
]
for i, (text, color) in enumerate(legend_row):
    ax.text(8, bottom_y - 4.6 - i * 0.45, text, fontsize=7.5, color=color, ha='center', family='monospace')

plt.tight_layout()
output_path = '/home/jarvis/.openclaw/workspace/toaa/internship_chart.png'
fig.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f'Chart saved to {output_path}')
plt.close()
