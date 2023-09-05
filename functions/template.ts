export function getTemplate({
    redirectPath,
    withError
  }: {
    redirectPath: string;
    withError: boolean;
  }): string {
    return `
    <!doctype html>
    <html lang="en" data-theme="dark">
  
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Дивнолесье</title>
       
  
        <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css">
  
        <style>
          body > main {
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: calc(100vh - 7rem);
            padding: 1rem 0;
            max-width: 600px;
          }
  
          .error {
            background: white;
            border-radius: 10px;
            color: var(--del-color);
            padding: 0.5em 1em;
          }
  
          h2 { color: var(--color-h2); }
        </style>
      </head>
  
      <body>
        <main>
          <article>
            <hgroup>
              <h1>Дивнолесье</h1>
              <h2>Введите пароль</h2>
            </hgroup>
            ${withError ? `<p class="error">Неверный пароль, попробуйте снова.</p>` : ''}
            <form method="post" action="/cfp_login">
              <input type="hidden" name="redirect" value="${redirectPath}" />
              <input type="password" name="password" placeholder="Пароль" aria-label="Пароль" autocomplete="current-password" required autofocus>
              <button type="submit" class="contrast">Отправиться в путешествие</button>
            </form>
            <a id="contact" title="Перейти в чат с куратором" href="https://vk.com/im?sel=-155728712">Хочу участвовать</a>
          </article>
        </main>
      </body>
  
    </html>
    `;
  }