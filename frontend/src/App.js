import React, { Component } from "react";
import DiaryList from "./DiaryList";
import DiaryButton from "./DiaryButton";
import axios from "axios";
import "./styles.css";
import { Link } from "react-router-dom";
import Button from "react-bootstrap/Button";
class App extends Component {
  componentDidMount() {
    axios
      .get("http://localhost:5000/diaries")
      .then((res) => {
        const characters = res.data; //.diaries;
        this.setState({ characters });
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
  makePostCall(character) {
    return axios
      .post("http://localhost:5000/diaries", character)
      .then(function (response) {
        console.log(response);
        response.status = 201;
        return true;
      })
      .catch(function (error) {
        console.log(error);
        return false;
      });
  }
  state = { characters: [] };
  handleSubmit = (character) => {
    this.makePostCall(character).then((callResult) => {
      if (callResult === true) {
        this.setState({ characters: [...this.state.characters, character] });
      }
    });
  };

  render() {
    const { characters } = this.state;
    return (
      <div class="centered">
        <h1>Welcome to MyDiary</h1>
        <DiaryList characterData={characters} />
        <DiaryButton handleSubmit={this.handleSubmit} />
      </div>
    );
  }
}
export default App;
