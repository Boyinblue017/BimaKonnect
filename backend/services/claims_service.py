CLAIM_GUIDES = {
    "motor": {
        "title": "Motor insurance claim guide",
        "documents": ["Your policy number and vehicle registration", "Driver's licence", "Photos or video of the damage and scene", "Police abstract or occurrence book reference where required", "Repair estimate or assessor details, if requested"],
        "steps": ["Protect people first. Move to a safe place only if it is safe to do so.", "Record the other driver's details, witnesses, location, and time. Do not admit liability at the scene.", "Notify your insurer or agent as soon as possible and follow its approved repair process.", "Keep copies of every form, report, photo, and receipt."],
        "urgent": "If anyone is injured or there is immediate danger, contact local emergency services first.",
    },
    "health": {
        "title": "Health insurance claim guide",
        "documents": ["Membership or policy number", "Hospital, clinic, and provider details", "Itemised medical bill and receipt", "Prescription, referral, or discharge summary if applicable", "Completed insurer claim form, if requested"],
        "steps": ["Seek appropriate medical care first, especially in an emergency.", "Call the insurer or use its approved provider network to check pre-authorisation requirements.", "Ask the provider for itemised bills and keep all receipts.", "Submit the documents through the insurer's stated channel and keep the claim reference number."],
        "urgent": "For a medical emergency, seek urgent care or contact local emergency services immediately.",
    },
    "crop": {
        "title": "Crop insurance claim guide",
        "documents": ["Policy number and farm/location details", "Photos or video showing the loss and date", "Planting, input, and harvest records where available", "Weather, pest, or incident details", "Inspection or extension officer report if requested"],
        "steps": ["Take clear photos before clearing, harvesting, or changing the affected area where safe.", "Notify the insurer quickly; some policies require notice before an assessor visit.", "Keep farm records and note the date, weather conditions, crop, and affected acreage.", "Do not dispose of evidence until your insurer confirms what it needs."],
        "urgent": "If there is flooding, fire, or another immediate hazard, prioritise your safety and follow local authority guidance.",
    },
    "business": {
        "title": "Business insurance claim guide",
        "documents": ["Policy number and business contact details", "Photos or video of loss or damage", "Stock, equipment, or sales records", "Receipts, invoices, or proof of ownership", "Police report or incident report where relevant"],
        "steps": ["Protect people and prevent further loss where it is safe to do so.", "Document damage, stock, equipment, and the incident before cleanup when possible.", "Notify your insurer promptly and ask before making non-emergency repairs or replacements.", "Keep all receipts for reasonable emergency protection costs and preserve business records."],
        "urgent": "If there is a fire, break-in, or immediate threat, contact local emergency services or authorities first.",
    },
    "life": {
        "title": "Life insurance claim guide",
        "documents": ["Policy number and policyholder details", "Death certificate or official notification required by the insurer", "Beneficiary identification and contact details", "Proof of relationship or beneficiary designation if requested", "Completed claim form and any documents listed by the insurer"],
        "steps": ["Contact the insurer or agent to open a claim and ask for its exact document list.", "Ask for a claim reference number and expected review process.", "Submit copies through the insurer's official channel; keep originals secure unless requested.", "Keep a record of every document sent and all conversations."],
        "urgent": "Take care of immediate family needs first. A trusted family member or licensed agent can help contact the insurer.",
    },
}


def get_claim_guidance(cover_type, incident):
    guide = CLAIM_GUIDES.get(cover_type)
    if not guide:
        return {
            "title": "General claim guide",
            "incident": incident,
            "urgent": "If someone is in danger, seek emergency help first.",
            "steps": ["Notify your insurer or agent promptly.", "Record what happened and keep relevant evidence.", "Ask the insurer for the correct claim form and document list."],
            "documents": ["Policy number", "Incident details", "Photos, receipts, or reports relevant to the loss"],
        }
    return {**guide, "incident": incident, "disclaimer": "This is a general guide, not a coverage decision. Your policy wording and insurer's instructions control your claim."}
