# Git Workflow и процесс разработки

## Модель ветвления

### Основные ветки

- **`main`** — production-ready код, защищена от прямых пушей
- **`p<nn>-<topic>`** — feature/fix ветки для заданий курса

### Именование веток

Формат: `p<nn>-<kebab-case-topic>`

Примеры:
- `p02-git-workflow` — настройка Git процессов
- `p03-security-audit` — аудит безопасности
- `p04-add-swagger-docs` — добавление документации

## Процесс разработки

### 1. Создание ветки

```bash
# Обновить main
git switch main
git pull

# Создать feature ветку
git switch -c p02-my-feature
```

### 2. Разработка

```bash
# Делаем изменения
# ...

# Проверяем локально
ruff check --fix .
black .
isort .
pytest -v
pre-commit run --all-files

# Коммитим
git add .
git commit -m "feat: add new feature"
```

### 3. Conventional Commits

Формат: `<type>: <description>`

**Типы:**
- `feat:` — новая функциональность
- `fix:` — исправление бага
- `refactor:` — рефакторинг без изменения поведения
- `test:` — добавление/изменение тестов
- `docs:` — изменения в документации
- `chore:` — рутинные задачи (обновление зависимостей и т.д.)
- `style:` — форматирование кода
- `perf:` — улучшение производительности
- `ci:` — изменения в CI/CD

**Примеры:**
```bash
git commit -m "feat: add user registration endpoint"
git commit -m "fix: resolve SQL injection in search query"
git commit -m "refactor: extract auth logic to separate service"
git commit -m "test: add integration tests for auth flow"
git commit -m "docs: update API documentation"
```

### 4. Push и создание PR

```bash
# Запушить ветку
git push -u origin p02-my-feature

# Открыть PR через GitHub UI
# или через GitHub CLI:
gh pr create --title "P02: My Feature" --body "..."
```

### 5. Code Review

- Заполните шаблон PR (что/почему/как проверял)
- Добавьте ревьюеров
- Приложите ссылку на [REVIEW_CHECKLIST.md](./REVIEW_CHECKLIST.md)
- Дождитесь зелёного CI
- Отвечайте на комментарии

### 6. Merge

После одобрения (approve) и зелёного CI:
- Мержим через GitHub UI кнопкой **Merge pull request**
- Выбираем **Squash and merge** для одного чистого коммита
- Удаляем feature ветку после мержа

### 7. Тег (для заданий курса)

```bash
git switch main
git pull
git tag P02
git push --tags
```

## Защита ветки main

Настроено через GitHub Settings → Branches:

- ✅ Require pull request before merging
- ✅ Require status checks to pass (CI / build)
- ✅ Require review from Code Owners
- ✅ Restrict who can push (только через PR)
- ⛔ No force push
- ⛔ No deletions

## Правила работы

### ✅ DO

- Одна ветка = одна законченная тема
- PR размером до 400-500 строк diff
- Заполнять шаблон PR полностью
- Проверять локально перед push
- Отвечать на комментарии ревьюеров
- Давать содержательные комментарии в ревью

### ❌ DON'T

- Прямые пуши в `main`
- Force push в чужие ветки
- Коммиты секретов/паролей
- PR без описания или тестов
- "LGTM" без аргументов в ревью
- Игнорирование замечаний ревьюеров

## Troubleshooting

### Конфликты при merge

```bash
# Обновить свою ветку из main
git switch p02-my-feature
git fetch origin
git rebase origin/main

# Разрешить конфликты
# ... редактируем файлы ...
git add .
git rebase --continue

# Force push (только в свою ветку!)
git push --force-with-lease
```

### Забыли запустить pre-commit

```bash
# Запустить pre-commit на последнем коммите
pre-commit run --all-files

# Добавить изменения
git add .
git commit --amend --no-edit

# Force push
git push --force-with-lease
```

### Нужно изменить последний коммит

```bash
# Внести изменения
git add .
git commit --amend

# Force push
git push --force-with-lease
```

## Полезные команды

```bash
# Посмотреть статус
git status

# Посмотреть diff
git diff

# Посмотреть историю
git log --oneline --graph

# Посмотреть изменения в конкретном коммите
git show <commit-hash>

# Откатить изменения в файле
git checkout -- <file>

# Удалить локальную ветку
git branch -d p02-old-feature

# Обновить список веток
git fetch --prune

# Интерактивный rebase (для продвинутых)
git rebase -i HEAD~3
```

## Дополнительные ресурсы

- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)
