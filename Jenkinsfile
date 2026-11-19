pipeline {
    agent any

    environment {
        VM_HOST = 'host.docker.internal'
        SSH_PORT = '2222'
        HTTP_PORT = '8001'
    }

    stages {
        stage('Lint & Test') {
            steps {
                echo '=== Шаг 1: Проверка кода линтером (Flake8) ==='
                sh 'flake8 app/ --select=F'

                echo '=== Шаг 2: Запуск автотестов (Pytest) ==='
                withCredentials([
                    string(credentialsId: 'ci-db-url', variable: 'DATABASE_URL'),
                    string(credentialsId: 'ci-redis-url', variable: 'REDIS_URL')
                ]) {
                    sh 'pytest -p no:cacheprovider tests/'
                }
            }
        }

        stage('Build') {
            steps {
                echo '=== Шаг 3: Сборка Docker-образа на Машине 1 ==='
                sh 'docker build -t weather-backend:latest .'
            }
        }

        stage('Deploy to Machine 2') {
            steps {
                echo '=== Шаг 4: Деплой на Машину 2 (Ubuntu VM) по SSH ==='
                withCredentials([usernamePassword(credentialsId: 'vm-ssh-credentials', usernameVariable: 'SSH_USER', passwordVariable: 'SSH_PASS')]) {
                    sh '''
                        sshpass -p "$SSH_PASS" ssh -p $SSH_PORT -o StrictHostKeyChecking=no "$SSH_USER@$VM_HOST" "cd project_sofad && git pull && docker compose up -d --build"
                    '''
                }
            }
        }

        stage('Smoke Test') {
            steps {
                echo '=== Шаг 5: Smoke-тест /health на Машине 2 ==='
                sleep 5
                // Пробуем до 10 раз с интервалом в 3 секунды, пока сервис окончательно не прогреется
                sh 'curl --retry 10 --retry-delay 3 --retry-all-errors -f http://$VM_HOST:$HTTP_PORT/health'
            }
        }
    }

    post {
        success {
            echo '=== Пайплайн успешно завершен! Проект развернут на Машине 2 ==='
        }
        failure {
            echo '=== Пайплайн упал с ошибкой! ==='
        }
    }
}