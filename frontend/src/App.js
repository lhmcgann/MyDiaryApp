import React, { Component } from "react";
import Home from "./components/Home";
import DiaryHome from "./components/DiaryHome";
import ViewEntry from "./components/ViewEntry";
import { BrowserRouter as Router, Route, Switch} from "react-router-dom";
import "./styles.css";
// import { Link } from "react-router-dom";
// import Button from "react-bootstrap/Button";
class App extends Component {
  render() {
      return (
    <Router>
      <Switch>
        <Route exact path="/">
          <Home />
        </Route>
        <Route path="/diaries/:d_id/entries/:e_id" render={(props) => <ViewEntry {...props}/>}/>
        <Route path="/diaries/:d_id" render={(props) => <DiaryHome {...props}/>}/>
      </Switch>
    </Router>
    )
  }
}
export default App;
