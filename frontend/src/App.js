import React, { Component } from "react";
import Home from "./components/Home";
import DiaryHome from "./components/DiaryHome";
import ViewEntry from "./components/ViewEntry";
import { BrowserRouter as Router, Route, Switch, Link} from "react-router-dom";
import axios from "axios";
import "./styles.css";
// import { Link } from "react-router-dom";
// import Button from "react-bootstrap/Button";
class App extends Component {
  render() {
      return (
      <Switch>
        <Route exact path="/">
          <Home />
        </Route>
        <Route path="/diary/:id"render={(props) => <DiaryHome {...props}/>}/>
        <Route path="entry/:e_id"render={(props) => <ViewEntry {...props}/>}/>
      </Switch>
    )
  }
}
export default App;
