CREATE TABLE uzytkownicy (
	id integer PRIMARY KEY AUTOINCREMENT,
	imie text NOT NULL,
	nazwisko text NOT NULL,
	tytul text NOT NULL,
	specjalnosc text NOT NULL,
	email text UNIQUE NOT NULL,
	screen text,
	obszary text NOT NULL --obszary wybrane do ankiety, wymienione po przecinku np. "wpn, kpn"
);

CREATE TABLE ankiety (
	id integer PRIMARY KEY AUTOINCREMENT,
	uzytkownik integer,
	obszar text NOT NULL,
	mapa text NOT NULL,
	uzasadnienie text NOT NULL,
	FOREIGN KEY(uzytkownik) REFERENCES uzytkownicy(id)
);

CREATE TABLE odpowiedzi (
	id integer PRIMARY KEY AUTOINCREMENT,
	ankieta_id integer,
	czynnik text NOT NULL, -- w przypadku przedzialow zostanie wpisany string "<min>, <max>"
	ocena NUMERIC NOT NULL,
	pewnosc NUMERIC NOT NULL,
	waga NUMERIC,
	FOREIGN KEY(ankieta_id) REFERENCES ankiety(id)
);	
