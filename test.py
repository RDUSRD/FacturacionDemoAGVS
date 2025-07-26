from locust import HttpUser, task, between

class PerformanceTest(HttpUser):
    wait_time = between(1, 1)  # Tiempo de espera entre peticiones (en segundos)

    @task
    def test_empresa_endpoint(self):
        self.client.get("/empresa/")  # Realiza una petición GET al endpoint

# Para ejecutar el script, usa el siguiente comando en la terminal:
# locust -f performance_test.py --host=https://fact.talentoonline.com