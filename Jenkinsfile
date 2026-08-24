pipeline {
    agent any

    environment {
        APP_NAME   = "addressbook-web"
        IMAGE_NAME = "local/addressbook-web"
        PATH       = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-access-token',
                    url: 'https://github.com/bus57790/addressbook-devops.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube-Server') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${env.APP_NAME} \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=**/*.html \
                            -Dsonar.python.version=3.11
                        """
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build \
                      -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                      -t ${IMAGE_NAME}:latest \
                      .
                """
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh """
                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --scanners vuln \
                      --exit-code 0 \
                      ${IMAGE_NAME}:${BUILD_NUMBER}
                """
            }
        }

        stage('Validate Compose') {
            steps {
                sh '''
                    echo "Validating Docker Compose configuration..."
                    docker compose config --quiet
                '''
            }
        }

        stage('Deploy to Local Server') {
            steps {
                sh '''
                    set -e

                    echo "Stopping existing containers..."
                    docker compose down || true

                    echo "Starting application..."
                    docker compose up -d --build

                    echo "Container status:"
                    docker compose ps -a
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "Waiting for application startup..."
                    sleep 5

                    echo "Container status:"
                    docker compose ps -a

                    echo "Checking PostgreSQL health..."
                    docker inspect \
                      --format='{{.State.Health.Status}}' \
                      addressbook_db

                    echo "Testing Address Book web application..."

                    if ! curl \
                        --fail \
                        --retry 10 \
                        --retry-delay 3 \
                        --retry-connrefused \
                        http://192.168.1.184:5000/; then

                        echo "========================================"
                        echo "WEB APPLICATION HEALTH CHECK FAILED"
                        echo "========================================"

                        echo "Container status:"
                        docker compose ps -a

                        echo "Web container logs:"
                        docker logs addressbook_web --tail 100 || true

                        echo "Database container logs:"
                        docker logs addressbook_db --tail 50 || true

                        exit 1
                    fi

                    echo "Application health check passed."
                '''
            }
        }

        stage('Seed Sample Users') {
            steps {
                sh '''
                    echo "Seeding sample contacts..."

                    docker exec -i addressbook_db \
                      psql -U postgres -d addressbook <<'EOF'

INSERT INTO contacts
    (full_name, phone, email, address)
VALUES
    (
        'Ada Lovelace',
        '+1-555-0101',
        'ada@example.com',
        '10 Binary Way, London, UK'
    ),
    (
        'Alan Turing',
        '+1-555-0102',
        'alan@example.com',
        '42 Enigma Ave, Bletchley, UK'
    ),
    (
        'Grace Hopper',
        '+1-555-0103',
        'grace@example.com',
        '1952 Compiler Rd, Arlington, VA'
    ),
    (
        'Linus Torvalds',
        '+1-555-0104',
        'linus@example.com',
        '100 Linux Blvd, Portland, OR'
    )
ON CONFLICT DO NOTHING;

EOF
                '''
            }
        }

        stage('Generate & Archive QR Artifacts') {
            steps {
                sh '''
                    echo "Generating QR codes..."

                    rm -rf sample_qr_codes

                    docker exec \
                      addressbook_web \
                      python generate_qr_codes.py

                    docker cp \
                      addressbook_web:/app/sample_qr_codes \
                      ./sample_qr_codes

                    echo "Generated QR files:"
                    ls -la sample_qr_codes
                '''

                archiveArtifacts(
                    artifacts: 'sample_qr_codes/*.png',
                    fingerprint: true
                )
            }
        }
    }

    post {

        success {
            withCredentials([
                string(
                    credentialsId: 'slack-webhook-url',
                    variable: 'SLACK_URL'
                )
            ]) {
                script {
                    def jsonText =
                        """{"text":"Pipeline Succeeded: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] - Application deployed successfully."}"""

                    writeFile(
                        file: 'slack.json',
                        text: jsonText
                    )

                    sh '''
                        curl \
                          --fail-with-body \
                          -sS \
                          -X POST \
                          -H 'Content-Type: application/json' \
                          --data @slack.json \
                          "$SLACK_URL" \
                          || echo "WARNING: Slack notification failed"
                    '''
                }
            }
        }

        failure {
            withCredentials([
                string(
                    credentialsId: 'slack-webhook-url',
                    variable: 'SLACK_URL'
                )
            ]) {
                script {
                    def jsonText =
                        """{"text":"Pipeline Failed: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] - Check Jenkins console output."}"""

                    writeFile(
                        file: 'slack.json',
                        text: jsonText
                    )

                    sh '''
                        curl \
                          --fail-with-body \
                          -sS \
                          -X POST \
                          -H 'Content-Type: application/json' \
                          --data @slack.json \
                          "$SLACK_URL" \
                          || echo "WARNING: Slack notification failed"
                    '''
                }
            }
        }

        always {
            cleanWs()
        }
    }
}
