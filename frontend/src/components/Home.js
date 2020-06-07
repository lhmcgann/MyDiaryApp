import React, { Component } from "react";
import DiaryList from "./DiaryList";
import DiaryButton from "./DiaryButton";
import axios from "axios";
class Home extends Component {

  state = { diaries: [] };

  componentDidMount() {
    axios
      .get("http://localhost:5000/diaries")
      .then((res) => {
        const diaries = res.data.diaries;
        console.log(diaries);
        this.setState({ diaries });
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
  handleSubmit = (title) => {
    this.makePostCall(title).then((callResult) => {
      if (callResult !== false) {
        this.setState({ diaries: [...this.state.diaries, callResult] });
      }
    });
  };
  makePostCall(title) {
    return axios
      .post("http://localhost:5000/diaries", title)
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
  makeDeleteCall(diary){
    return axios.delete('http://localhost:5000/diaries/'+diary._id)
    .then(function (response) {
      console.log(response);
      return true;
    })
    .catch(function (error) {
      console.log(error);
      return false;
    });
  }
  removeDiary = index => {
    const {diaries} = this.state;
    const diary = diaries[index];
    this.makeDeleteCall(diary).then((callResult) => {
      if (callResult !== false){
        this.setState({
          diaries: diaries.filter((diary, i) => {
            return i !== index
          }),
        })
      }
    });
  }
  render() {
    const { diaries } = this.state;
    return (
      <div className="centered">
        <h1>Welcome to MyDiary</h1>
        <DiaryList diaryData={diaries} removeDiary={this.removeDiary}/>
        <DiaryButton handleSubmit={this.handleSubmit}/>
      </div>
    );
  }
}
export default Home;
