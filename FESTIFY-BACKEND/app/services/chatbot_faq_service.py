from sqlalchemy import text
from app.extensions import db
from app.models.chatbot_faq import ChatbotFAQ


def _normalise(row):
    if isinstance(row, dict):
        return {"faq_id": row.get("faq_id"), "question": row.get("question"),
                "answer": row.get("answer"), "category": row.get("category"),
                "keywords": row.get("keywords")}
    return {"faq_id": row.faq_id, "question": row.question, "answer": row.answer,
            "category": row.category, "keywords": row.keywords}


def get_all_faqs(category=None):
    """Read FAQ rows from the model's festify schema, then public as a legacy fallback."""
    try:
        query = ChatbotFAQ.query.order_by(ChatbotFAQ.faq_id.asc())
        if category:
            query = query.filter_by(category=category)
        rows = query.all()
        if rows:
            result = [_normalise(row) for row in rows]
            return {"success": True, "faqs": result, "count": len(result)}, 200
    except Exception:
        db.session.rollback()

    # Existing installations sometimes created chatbot_faqs in public before the
    # model was moved to festify. Read that table too, without changing the model.
    try:
        sql = "SELECT faq_id, question, answer, category, keywords FROM public.chatbot_faqs"
        params = {}
        if category:
            sql += " WHERE category = :category"
            params["category"] = category
        sql += " ORDER BY faq_id ASC"
        rows = db.session.execute(text(sql), params).mappings().all()
        result = [_normalise(dict(row)) for row in rows]
        return {"success": True, "faqs": result, "count": len(result),
                "source": "public" if result else "festify"}, 200
    except Exception as exc:
        db.session.rollback()
        return {"success": False, "message": "Unable to load FAQ records from festify.chatbot_faqs or public.chatbot_faqs",
                "error": str(exc), "faqs": [], "count": 0}, 500


def search_faq(query_text):
    if not query_text or not str(query_text).strip():
        return {"success": True, "matches": [], "message": "Enter a question to search."}, 200
    terms = [term for term in str(query_text).lower().split() if len(term) > 2]
    payload, status = get_all_faqs()
    if status != 200:
        return {"success": False, "matches": [], "message": payload.get("message", "Unable to search FAQs")}, status
    scored = []
    for row in payload["faqs"]:
        haystack = " ".join([row.get("question") or "", row.get("answer") or "",
                             row.get("category") or "", row.get("keywords") or ""]).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, row))
    scored.sort(key=lambda pair: (-pair[0], pair[1].get("faq_id") or 0))
    matches = [row for _, row in scored[:5]]
    return {"success": True, "matches": matches,
            "message": "" if matches else "No matching FAQ found. Please contact your event organizer."}, 200


def create_faq(data):
    if not data.get("question") or not data.get("answer"):
        return {"success": False, "message": "question and answer are required"}, 400
    try:
        faq = ChatbotFAQ(question=data["question"], answer=data["answer"], category=data.get("category"), keywords=data.get("keywords"))
        db.session.add(faq); db.session.commit()
        return {"success": True, "message": "FAQ created successfully", "faq_id": faq.faq_id}, 201
    except Exception as exc:
        db.session.rollback()
        return {"success": False, "message": "Failed to create FAQ", "error": str(exc)}, 500


def update_faq(faq_id, data):
    faq = db.session.get(ChatbotFAQ, faq_id)
    if not faq: return {"success": False, "message": "FAQ not found"}, 404
    for field in ["question", "answer", "category", "keywords"]:
        if field in data: setattr(faq, field, data[field])
    try:
        db.session.commit(); return {"success": True, "message": "FAQ updated successfully"}, 200
    except Exception as exc:
        db.session.rollback(); return {"success": False, "message": "Failed to update FAQ", "error": str(exc)}, 500


def delete_faq(faq_id):
    faq = db.session.get(ChatbotFAQ, faq_id)
    if not faq: return {"success": False, "message": "FAQ not found"}, 404
    try:
        db.session.delete(faq); db.session.commit()
        return {"success": True, "message": "FAQ deleted successfully"}, 200
    except Exception as exc:
        db.session.rollback(); return {"success": False, "message": "Failed to delete FAQ", "error": str(exc)}, 500
