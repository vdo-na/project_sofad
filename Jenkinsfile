pipeline {
    agent any

    environment {
        VM_IP = '192.168.1.6'
    }

    stages {
        stage('Lint & Test') {
            steps {
                echo '=== Шаг 1: Проверка кода линтером (Flake8) ==='
                sh 'flake8 app/ --select=F'

                echo '=== Шаг 2: Запуск автотестов (Pytest) ==='
                sh 'pytest -p no:cacheprovider tests/'
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
                        sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$SSH_USER@$VM_IP" "cd project_sofad && git pull && docker compose up -d --build"
                    '''
                }
            }
        }

        stage('Smoke Test') {
            steps {
                echo '=== Шаг 5: Smoke-тест /health на Машине 2 ==='
                sleep 5
                sh 'curl -f http://192.168.1.6:8000/health'
            }
        }
    }

    post {
        success {
            echo '=== Пайплайн успешно завершен! Проект развернут на Машине 2 ==='
        }
        failure {
            echo '=== Пайплайн упал с ошибкой! Деплой отменен ==='
        }
    }
}