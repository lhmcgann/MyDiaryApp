import React, { Component } from "react";
import DiaryList from "./DiaryList";
import axios from "axios";
import { Link } from "react-router-dom";
class App extends Component {
  state = {
    characters: [],
  };
  componentDidMount() {
    axios
      .get(`http://localhost:5000/users/`)
      .then((res) => {
        const characters = res.data.users_list;
        this.setState({ characters });
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
  makePostCall(character) {
    return axios
      .post("http://localhost:5000/users", character)
      .then(function (response) {
        console.log(response);
        response.status = 201;
        return response.data;
      })
      .catch(function (error) {
        console.log(error);
        return false;
      });
  }
  makeDeleteCall(character) {
    return axios
      .delete("http://localhost:5000/users/" + character.id)
      .then(function (response) {
        console.log(response);
        return true;
      })
      .catch(function (error) {
        console.log(error);
        return false;
      });
  }
  render() {
    const { characters } = this.state;
    return (
      <div class="centered">
        <h1>Welcome to MyDiary</h1>
        <DiaryList characterData={characters} />
        <Link to="/new-diary/">
          <button class="button1">+ Add Diary</button>
        </Link>
      </div>
    );
  }
}
export default App;
