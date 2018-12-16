# html-css-processor
Лабораторана з предмета "Метапрограмування" - Варіант 24

***Опис***

З вказаного HTML файлу: 
1) генерує пакет, у модулях якого містяться класи, ієрархія яких відповідає ієрархії HTML тегів у
вказаному файлі (див. `generated/packages`).
2) на основі ієрархії згенерованих класів генерує HTML-документ (див. `generated/html`).

Використання:
```bash
C:\Users\Moon Light\PycharmProjects\Meta>python main.py
Enter HTML file path (e.g 'resources/index.html'): resources/index.html
Generating package 'index'
Package generated: ./generated/packages/index
Generating HTML from 'index' package
HTML file generated: ./generated/html/index.html
```