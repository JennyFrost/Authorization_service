### Сервис API_GATEWAY

Сервис выступает в роли общего хаба, принимает все входящие запросы
и перенаправляет их в другие сервисы.

Цель такого подхода разграничить зону ответсвенности разных сервисов, чтобы каждый
сервис отчечал за свои действия и не было небходимости расширять уже написанный сервис.

Например сервис api_gateway принимает входящий запрос на просмотр фильма
* сначала он отправит запрос в сервис auth_api, получит расшифровку токена
* потом в расшифровке проверит роль пользователя и в зависимости от роли пользователя сделает запрос в сервис фильмов 
или вернет ошибку недостаточно прав для просмотра


Было интересно реализовать и проверить как работает такой подход, сейчас мы им не пользуемся он написан для будущего
масштабирования проекта