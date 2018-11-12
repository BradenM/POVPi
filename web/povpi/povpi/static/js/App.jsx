// App.jsx

import React from 'react';

export default class App extends React.Component {
  get_url(page) {
    let url = window.location.href + page;
    return url;
  }

  render() {
    return (
      <div>
        <h1>Enter a message</h1>
        <form action={this.get_url('change')} method="POST">
          <label>
            Message:
            <input type="text" name="display" />
          </label>
          <input type="submit" value="Submit" />
        </form>
        <form action={this.get_url('toggle')} method="post">
          <label>
            Toggle Pi:
            <input type="submit" name="on" value="ON" />
            <input type="submit" name="off" value="OFF" />
          </label>
        </form>
      </div>
    );
  }
}
