curl -X POST "http://localhost:8000/inspect" \
     -H "Content-Type: application/json" \
     -d '{"sender": "jan.kowalski@example.com", "message": "Hej, kup teraz nasz super produkt za 99 zł!"}'