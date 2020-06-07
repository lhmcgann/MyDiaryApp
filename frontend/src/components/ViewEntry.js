import React, { Component } from "react";
import "../styles.css";
import axios from "axios";
class ViewEntry extends Component {
  componentDidMount(){
    axios
      .get("http://localhost:5000/diaries/"+this.props.match.params.d_id+"/entries/"
          +this.props.match.params.e_id)
      .then((res) => {
        const entry = res.data;
        this.setState({ title: entry.title, text: entry.textBody});
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
state = {title: '', text: '',};
handleChange(e) {
    this.setState({
      text :e.target.value
    });
  }
putProgress(title, textBody, tags){
  axios
    .put("http://localhost:5000/diaries/"+this.props.match.params.d_id+"/entries/"
        +this.props.match.params.e_id, {title: title, text: textBody, tags: tags})
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
render() {
 const title = this.state.title;
 const textBody = this.state.text;
 const tags = [];
 return (
   <div className="centered">
   <h1>{title}</h1>
   <textarea
    cols="30"
    rows="15"
    value={textBody}
    onChange={e => this.handleChange(e)}
   />
   <input type="button" value="Save" onClick={this.putProgress(title, textBody, tags)} />
   </div>
  );
  }
}
export default ViewEntry;
