Save your https://openweathermap.org API key in .env
WEATHER_API_KEY=PUT_IT_HERE

You need Docker to run this app:
docker build -t matakov/temp:1.1 .
docker run -ti matakov/temp:1.1
