QUESTION_GEN_TEMPLATE = """\
Hier ist der Kontext:
{context_str}

Angesichts der kontextuellen Informationen, \
erzeugen Sie {num_questions} Fragen, zu denen dieser Kontext \
spezifische Antworten liefern kann, die wahrscheinlich nicht anderswo zu finden sind.

Höherstufige Zusammenfassungen des umgebenden Kontexts können ebenfalls angegeben werden. \
Versuchen Sie, diese Zusammenfassungen zu nutzen, um bessere Fragen zu generieren, \
auf die dieser Kontext antworten kann.
"""

SUMMARY_EXTRACT_TEMPLATE = """\
Hier ist der Inhalt des Abschnitts:
{context_str}

Fassen Sie die Schlüsselthemen und -entitäten des Abschnitts zusammen. \

Zusammenfassung: """

TEXT_QUESTION_TEMPLATE = """\
Kontextinformationen stehen unten.\
---------------------\
{context_str}
---------------------\
Angesichts der Kontextinformationen und ohne Vorwissen, erzeugen Sie nur Fragen, die auf der folgenden Anfrage basieren. \
{query_str}
"""

TEXT_QA_TEMPLATE = """\
Kontextinformationen stehen unten.\
---------------------\
{context_str}
---------------------\
Angesichts der Kontextinformationen und ohne Vorwissen, beantworten Sie die Anfrage.\
Anfrage: {query_str}
Antwort:
"""

EVAL_QUESTION_GEN_TEMPLATE = """
Sie sind Lehrer/Professor. Ihre Aufgabe ist es, 
{num_questions_per_chunk} Fragen für ein bevorstehendes 
Quiz/eine bevorstehende Prüfung zu erstellen. Die Fragen sollten in 
ihrer Art vielfältig über das Dokument verteilt sein. 
Beschränken Sie die Fragen auf die bereitgestellten Kontextinformationen.
"""
