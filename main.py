# =========================================================
# LISCA AI – Version 1.3 (CONSOLIDÉE FINALE)
# Gouvernance ONG Cancer – Console UX PRO
# =========================================================

from datetime import date, datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage

# =========================
# PARAMÈTRES LISCA
# =========================
SEUIL_PREVALIDATION_SG = 7

EMAIL_EXPEDITEUR = "moubarak1994@yahoo.fr"
MOT_DE_PASSE_APP = "fedtgcqvedgzddtj"

EMAILS = {
    "presidente": "ibrahim.madougou@yahoo.fr",
    "sg": "pecrites@gmail.com",
    "secretaire": "lnlcniger@gmail.com",
    "assistant_social": "besttconsult@gmail.com",
    "partenaires": "partenaires@lisca.sn"
}

# =========================
# MODELES
# =========================
class DossierPatient:
    def __init__(self, nom, type_cancer, priorite_sociale, urgent_medical):
        self.nom = nom
        self.type_cancer = type_cancer
        self.priorite_sociale = priorite_sociale
        self.urgent_medical = urgent_medical


class RendezVous:
    def __init__(self, titre, date_heure, participants):
        self.titre = titre
        self.date_heure = date_heure
        self.participants = participants


class Depense:
    def __init__(self, categorie, montant):
        self.categorie = categorie
        self.montant = montant


# =========================
# AGENTS MÉTIERS
# =========================
class AgentPreValidationSG:
    def dossiers_urgents(self, dossiers):
        return [
            d for d in dossiers
            if d.urgent_medical or d.priorite_sociale >= SEUIL_PREVALIDATION_SG
        ]


class AgentAgenda:
    def rappels_24h(self, rendezvous):
        maintenant = datetime.now()
        return [
            r for r in rendezvous
            if 0 <= (r.date_heure - maintenant).total_seconds() <= 86400
        ]


class AgentEmail:
    def envoyer(self, sujet, message, destinataires, piece_jointe=None):
        msg = EmailMessage()
        msg["Subject"] = sujet
        msg["From"] = EMAIL_EXPEDITEUR
        msg["To"] = ", ".join(destinataires)
        msg.set_content(message)

        if piece_jointe:
            with open(piece_jointe, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="pdf",
                    filename=piece_jointe
                )

        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as serveur:
            serveur.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_APP)
            serveur.send_message(msg)


class AgentRapportJournalier:
    def generer_pdf(self, dossiers, urgents):
        nom_pdf = f"rapport_LISCA_{date.today()}.pdf"
        c = canvas.Canvas(nom_pdf, pagesize=A4)
        c.setFont("Helvetica", 10)

        y = A4[1] - 50
        lignes = [
            "RAPPORT JOURNALIER – LISCA",
            f"Date : {date.today()}",
            "=" * 60,
            f"Dossiers reçus : {len(dossiers)}",
            f"Dossiers urgents : {len(urgents)}",
            "",
            "DOSSIERS URGENTS"
        ]

        for d in urgents:
            lignes.extend([
                "-" * 60,
                f"Patient : {d.nom}",
                f"Cancer : {d.type_cancer}",
                f"Priorité sociale : {d.priorite_sociale}",
                f"Urgence médicale : {'OUI' if d.urgent_medical else 'NON'}"
            ])

        lignes.append("")
        lignes.append(
            "Les dossiers urgents ont été automatiquement identifiés selon les critères validés par la LISCA."
        )

        for ligne in lignes:
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = A4[1] - 50
            c.drawString(40, y, ligne)
            y -= 12

        c.save()
        return nom_pdf


# =========================
# DASHBOARDS PAR RÔLE
# =========================
class DashboardAssistantSocial:
    def afficher(self, dossiers):
        print("\n👩‍🤝‍👩 ASSISTANT SOCIAL")
        print("-" * 60)
        for d in dossiers:
            if d.priorite_sociale >= 4:
                print(f"{d.nom} | {d.type_cancer} | Priorité {d.priorite_sociale}")
        print("➡️ Étude sociale avant prise en charge\n")


class DashboardSecretaire:
    def afficher(self):
        print("\n🧑‍💼 SECRÉTARIAT")
        print("-" * 60)
        print("📩 Emails | 📅 Agenda | 📄 Rapports | ⏰ Rappels\n")


class DashboardSG:
    def afficher(self, dossiers, urgents, depenses):
        print("\n🧑‍⚖️ SECRÉTAIRE GÉNÉRAL – VUE GLOBALE")
        print("=" * 70)
        print(f"Dossiers totaux : {len(dossiers)}")
        print(f"Dossiers urgents : {len(urgents)}")
        print(f"Dépenses enregistrées : {sum(d.montant for d in depenses)} FCFA")
        print("Modules : Social | Médicaments | Dépistage | Sensibilisation | Partenariats | Finances")
        print("=" * 70 + "\n")


class DashboardPresidente:
    def afficher(self, dossiers, urgents):
        print("\n👩‍⚕️ PRÉSIDENCE – SYNTHÈSE")
        print("-" * 60)
        print(f"Activité globale : {len(dossiers)} dossiers")
        print(f"Urgences : {len(urgents)}")
        print("Rapports | Finances | Partenariats\n")


class DashboardPartenaires:
    def afficher(self, depenses):
        print("\n🤝 PARTENAIRES – TRANSPARENCE")
        print("-" * 60)
        total = sum(d.montant for d in depenses)
        for d in depenses:
            print(f"{d.categorie} : {d.montant} FCFA")
        print(f"TOTAL : {total} FCFA\n")


# =========================
# EXECUTION PRINCIPALE
# =========================
if __name__ == "__main__":

    dossiers = [
        DossierPatient("Aminata S.", "Cancer du sein", 10, True),
        DossierPatient("Fatou D.", "Cancer du col", 2, False),
        DossierPatient("Mariama K.", "Cancer du sein", 7, False),
    ]

    depenses = [
        Depense("Médicaments", 150000),
        Depense("Transport patients", 80000),
        Depense("Sensibilisation", 120000),
    ]

    rendezvous = [
        RendezVous(
            "Réunion stratégique LISCA",
            datetime.now() + timedelta(hours=6),
            ["presidente", "sg"]
        )
    ]

    agent_sg = AgentPreValidationSG()
    urgents = agent_sg.dossiers_urgents(dossiers)

    agent_rapport = AgentRapportJournalier()
    pdf = agent_rapport.generer_pdf(dossiers, urgents)

    AgentEmail().envoyer(
        "Rapport journalier LISCA",
        "Veuillez trouver le rapport journalier LISCA en pièce jointe.",
        [EMAILS["presidente"], EMAILS["sg"]],
        pdf
    )

    DashboardAssistantSocial().afficher(dossiers)
    DashboardSecretaire().afficher()
    DashboardSG().afficher(dossiers, urgents, depenses)
    DashboardPresidente().afficher(dossiers, urgents)
    DashboardPartenaires().afficher(depenses)

    print("✅ LISCA AI – SYSTÈME OPÉRATIONNEL COMPLET")
