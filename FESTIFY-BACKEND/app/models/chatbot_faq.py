from app.extensions import db


class ChatbotFAQ(db.Model):
    __tablename__ = "chatbot_faqs"
    __table_args__ = {"schema": "festify"}

    faq_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    keywords = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<ChatbotFAQ {self.faq_id}: {self.question}>"