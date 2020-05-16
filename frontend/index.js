import './custom.scss';
import React from 'react'
import ReactDOM from 'react-dom'
import 'bootstrap/dist/css/bootstrap.min.css';
import {BrowserRouter as Router, Route, Link, Switch } from 'react-router-dom';
import App from './App'
import Welcome from './Welcome'
import DiaryHome from './DiaryHome'
import NewDiary from './NewDiary'
import ViewEntry from './ViewEntry'
import NewEntry from './NewEntry'
import './index.css'

const routes = (
  <Router>
    <div>
      <Switch>
         <Route path="/" exact component={App} />
         <Route path="/diary/:name/:id" component={DiaryHome} />
         <Route path="/new-diary" component={NewDiary} />
         <Route path="/entry/:name" component={ViewEntry} />
         <Route path="/new-entry" component={NewEntry} />
       </Switch>
    </div>
  </Router>

)
ReactDOM.render(routes, document.getElementById('root'))
