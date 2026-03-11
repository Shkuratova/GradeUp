INSERT into departments (department_name) VALUES
('Отдел разработки'),
('Отдел тестирования'),
('Отдел аналитики'),
('Отдел обучения');

INSERT INTO positions (position) VALUES
('Python-разработчик'),
('1С-разработчик'),
('Аналитик'),
('Тестировщик'),
('Тимлид'),
('Специалист по обучению');

INSERT INTO users (email, last_name, first_name, patronymic, password, position_id, department_id, role_id) VALUES
-- Разарабокта
('morozov.av@example.com', 'Морозов', 'Артем', 'Валерьевич', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 5, 1, 2),
('sokоlova.ad@example.com', 'Соколова', 'Анна', 'Дмитриевна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 1, 1, 1),
('volkov.ki@example.com', 'Волков', 'Кирилл', 'Игоревич', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 1, 1, 1),
('zayceva.ep@example.com', 'Зайцева', 'Елизавета', 'Павловна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 1, 1, 1),
('belov.gs@example.com', 'Белов', 'Григорий', 'Сергеевич', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 1, 1, 1),

('novikova.mu@example.com', 'Новикова', 'Марина', 'Юрьевна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 2, 1, 1),
('makarov.ie@example.com', 'Макаров', 'Илья', 'Евгеньевич', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 2, 1, 1),
('petrova.ki@example.com', 'Петрова', 'Ксения', 'Ильинична', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 2, 1, 1),
('federov.ak@example.com', 'Федоров', 'Арсений', 'Константинович', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 2, 1, 1),
('melnikova.ov@example.com', 'Мельникова', 'Ольга', 'Васильевна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 2, 1, 1),
-- Тестирование
('orlova.vm@example.com', 'Орлова', 'Виктория', 'Максимовна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 5, 2, 2),
('tihonov.ro@example.com', 'Тихонов', 'Роман', 'Олегович', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 4, 2, 1),
('komarova.aa@example.com', 'Комарова', 'Алиса', 'Андреевна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 4, 2, 1),
('efimov.np@example.com', 'Ефимов', 'Николай', 'Петрович', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 4, 2, 1),
-- Аналитики
('semenova.da@example.com', 'Семенова', 'Дарья', 'Александровна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 5, 3, 2),
('kuznecov.da@example.com', 'Кузнецов', 'Денис', 'Анатольевич', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 3, 3, 1),
('ivanova.sv@example.com', 'Иванова', 'София', 'Владимировна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 3, 3, 1),
('zhukov.sb@example.com', 'Жуков', 'Станислав', 'Борисович', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 3, 3, 1),
-- СПО
('danilov.vr@example.com', 'Данилов', 'Вадим', 'Романович', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 6, 4, 3),
('stepanova.eg@example.com', 'Степанова', 'Екатерина', 'Геннадьевна', '$2b$12$ccdnjs2m8bYldl.UPbQ.depo6hhQRuwRaRKah1tjDu8MlFPBS96W6', 6, 4, 3);






 SELECT skills.title, anon_1.num_stages
FROM (SELECT certifications.skill_id AS skill_id, count(certifications.skill_id) AS num_stages
FROM certifications GROUP BY certifications.skill_id) AS anon_1 JOIN skills ON skills.id = anon_1.skill_id;




