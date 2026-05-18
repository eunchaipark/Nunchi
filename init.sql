-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 사용자
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    kakao_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    has_pin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 플랜
CREATE TABLE IF NOT EXISTS user_plans (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    plan VARCHAR(10) NOT NULL,
    voice_limit_sec INTEGER NOT NULL,
    text_limit INTEGER NOT NULL,
    text_max_length INTEGER NOT NULL
);

-- 보호자 접근 권한
CREATE TABLE IF NOT EXISTS guardian_access (
    guardian_id INTEGER REFERENCES users(id),
    elder_id INTEGER REFERENCES users(id),
    can_view_score BOOLEAN DEFAULT TRUE,
    can_view_content BOOLEAN DEFAULT FALSE,
    granted_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (guardian_id, elder_id)
);

-- 대화 원문
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    encrypted_content TEXT NOT NULL,
    encrypted_fixed_content TEXT,
    encrypted_ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 벡터 임베딩 (RAG)
CREATE TABLE IF NOT EXISTS conversation_vectors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    conversation_id INTEGER REFERENCES conversations(id) NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 감정 점수
CREATE TABLE IF NOT EXISTS emotion_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    conversation_id INTEGER REFERENCES conversations(id) NOT NULL,
    loneliness FLOAT NOT NULL,
    anxiety FLOAT NOT NULL,
    depression FLOAT NOT NULL,
    vitality FLOAT NOT NULL,
    connection FLOAT NOT NULL,
    hope FLOAT NOT NULL,
    overall_risk FLOAT NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- 사용량
CREATE TABLE IF NOT EXISTS usage_logs (
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    voice_seconds INTEGER DEFAULT 0,
    text_count INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, date)
);

-- 알림 이력
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    guardian_id INTEGER REFERENCES users(id) NOT NULL,
    trigger_score FLOAT NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    channel VARCHAR(10) NOT NULL
);


-- =====================
-- 테스트 데이터
-- =====================

-- 노인 사용자 3명
INSERT INTO users (kakao_id, name, has_pin) VALUES
('kakao_elder_1', '김영수', true),
('kakao_elder_2', '이순자', true),
('kakao_elder_3', '박철수', false);

-- 보호자 2명
INSERT INTO users (kakao_id, name, has_pin) VALUES
('kakao_guardian_1', '김민준', false),
('kakao_guardian_2', '이지은', false);

-- 복지사 1명
INSERT INTO users (kakao_id, name, has_pin) VALUES
('kakao_welfare_1', '최복지', false);

-- 플랜 설정 (id 1~9)
INSERT INTO user_plans (user_id, plan, voice_limit_sec, text_limit, text_max_length) VALUES
(1, 'free', 120, 5, 100),
(2, 'basic', 600, 20, 300),
(3, 'free', 120, 5, 100),
(4, 'free', 120, 5, 100),
(5, 'free', 120, 5, 100),
(6, 'free', 120, 5, 100),
(7, 'free', 120, 5, 100),
(8, 'free', 120, 5, 100),
(9, 'free', 120, 5, 100),
(10, 'free', 120, 5, 100);

-- 보호자 연결
-- 김민준 → 김영수 담당
-- 이지은 → 이순자, 박철수 담당
INSERT INTO guardian_access (guardian_id, elder_id, can_view_score, can_view_content) VALUES
(4, 1, true, false),
(5, 2, true, false),
(5, 3, true, false);

-- 대화 데이터 (김영수)
INSERT INTO conversations (user_id, encrypted_content, encrypted_fixed_content, encrypted_ai_response) VALUES
(1, '오늘 밥을 머겄는디 혼자먹으니께 맛이 업네', '오늘 밥을 먹었는데 혼자 먹으니 맛이 없네', '오늘 혼자 드셨군요. 무슨 반찬 드셨어요?'),
(1, '자식들이 연락이 업서 서운허이', '자식들이 연락이 없어 서운해', '연락이 뜸하면 많이 서운하시죠. 마지막으로 연락받은 게 언제예요?'),
(1, '오늘은 날씨가 좋아서 산책을 했당께', '오늘은 날씨가 좋아서 산책을 했어', '산책하셨군요! 어디까지 다녀오셨어요?');

-- 대화 데이터 (이순자)
INSERT INTO conversations (user_id, encrypted_content, encrypted_fixed_content, encrypted_ai_response) VALUES
(2, '머리가 아프고 밥도 못 먹겄어', '머리가 아프고 밥도 못 먹겠어', '많이 불편하시겠어요. 언제부터 그러셨어요?'),
(2, '오늘 복지관에서 친구들이랑 놀았어', '오늘 복지관에서 친구들이랑 놀았어', '복지관에서 즐거운 시간 보내셨군요! 무슨 활동 하셨어요?');

-- 감정 점수 (김영수 - 대화 1,2,3)
INSERT INTO emotion_logs (user_id, conversation_id, loneliness, anxiety, depression, vitality, connection, hope, overall_risk) VALUES
(1, 1, 8.0, 5.0, 6.0, 3.0, 2.0, 3.0, 7.2),
(1, 2, 9.0, 6.0, 7.0, 2.0, 1.0, 2.0, 8.1),
(1, 3, 4.0, 2.0, 3.0, 7.0, 6.0, 7.0, 3.2);

-- 감정 점수 (이순자 - 대화 4,5)
INSERT INTO emotion_logs (user_id, conversation_id, loneliness, anxiety, depression, vitality, connection, hope, overall_risk) VALUES
(2, 4, 6.0, 7.0, 5.0, 3.0, 3.0, 4.0, 6.5),
(2, 5, 2.0, 1.0, 2.0, 8.0, 9.0, 8.0, 1.8);

-- 사용량
INSERT INTO usage_logs (user_id, date, voice_seconds, text_count) VALUES
(1, CURRENT_DATE, 45, 3),
(2, CURRENT_DATE, 120, 2),
(3, CURRENT_DATE, 0, 0);

-- 알림 이력
INSERT INTO notification_logs (user_id, guardian_id, trigger_score, channel) VALUES
(1, 4, 8.1, 'email'),
(2, 5, 6.5, 'email');