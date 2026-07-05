from backend.utils.ai import client as groq_client


class EinsteinBot:
    """
    Einstein-bot logic for active scam-baiting.
    Modular design inspired by honeybot.
    """

    def __init__(self):
        self.system_prompt = (
            "You are 'Einstein-bot', a hyper-intelligent AI honeypot. "
            "Your goal is to waste scammers' time by acting as a confused, "
            "vulnerable, but talkative elderly person. "
            "Ask redundant questions, misspell things occasionally, and "
            "give long, winding stories that lead nowhere. "
            "NEVER give real information. If they ask for OTP, give a fake 6-digit number "
            "that changes every time. Keep them on the line for as long as possible."
        )

    async def generate_response(self, input_text: str) -> str:
        try:
            # Check if client exists
            if not groq_client:
                return "Oh dear, my hearing aid is buzzing. What did you say?"

            completion = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": input_text}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Honeypot Error: {e}")
            return "Oh dear, my internet is acting up again. What did you say?"


einstein_bot = EinsteinBot()
