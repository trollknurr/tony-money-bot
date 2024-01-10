format:
	black tony_money_bot
	ruff check --fix-only ./tony_money_bot

lint:
	ruff check ./tony_money_bot

rebuild:
	docker-compose up -d --build bot

logs:
	docker-compose logs -f bot

shell:
	docker-compose exec bot bash