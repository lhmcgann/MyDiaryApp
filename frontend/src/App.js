import React, { Component } from "react";
import Home from "./components/Home";
import DiaryHome from "./components/DiaryHome";
import EntryList from "./components/EntryList";
import { BrowserRouter as Router, Route, Switch, Link} from "react-router-dom";
import axios from "axios";
import "./styles.css";
// import { Link } from "react-router-dom";
// import Button from "react-bootstrap/Button";
class App extends Component {
  render() {
      const characters = this.state;
      return (
      <Switch>
        <Route exact path="/">
          <Home />
        </Route>
        <Route path="/diary/:id">
          <DiaryHome />
        </Route>
      </Switch>
    )
  }
}
export default App;
