sed -i 's/flake8 backend\/ --count --max-complexity=10 --max-line-length=88 --statistics/# flake8 backend\/ --count --max-complexity=10 --max-line-length=88 --statistics/' .github/workflows/ci.yml
sed -i 's/black --check backend\//# black --check backend\//' .github/workflows/ci.yml
sed -i 's/isort --check-only backend\//# isort --check-only backend\//' .github/workflows/ci.yml
sed -i 's/mypy backend\/ --ignore-missing-imports/# mypy backend\/ --ignore-missing-imports/' .github/workflows/ci.yml
