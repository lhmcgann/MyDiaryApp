import React, { Component } from "react";
import "../styles.css";
import TagList from "./TagList";
import axios from "axios";
class ViewEntry extends Component {
  componentDidMount(){
    axios
      .get("http://localhost:5000/diaries/"+this.props.match.params.d_id+"/entries/"
          +this.props.match.params.e_id)
      .then((res) => {
        const entry = res.data;
        this.setState({ title: entry.title, text: entry.textBody, tags: entry.tags});
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
state = {title: '', text: '', tags: [], name: '',};
handleChange(e) {
    this.setState({
      text :e.target.value
    });
  }
  addTag = () => {
    if (this.state.name !== "") {
      this.addTagName(this.state.name);
      this.setState({name: '',});
    }
  };
tagChange(e){
  this.setState({
    name :e.target.value
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
addTagName(name){
  const tags = this.state.tags;
  tags.push(name);
  axios
    .post("http://localhost:5000/diaries/"+this.props.match.params.d_id+"/entries/"
        +this.props.match.params.e_id+"/tags", {title: this.state.title,
          text: this.state.text,
          tags: tags})
        .then(function (response) {
          console.log(response);
          response.status = 201;
          return response.data;
        })
        .catch(function (error) {
          console.log(error);
          return false;
        })
}
render() {
 const title = this.state.title;
 const textBody = this.state.text;
 const name = this.state.name;
 const tags = this.state.tags;
 return (
   <div className="centered">
   <h1>{title}</h1>
   <label htmlFor="Tags">Enter Tag Name</label>
   <textarea
    cols="25"
    rows="1"
    label="Tag Name"
    value={name}
    onChange={e => this.tagChange(e)}
   />
   <label htmlFor="Text">Enter Text</label>
   <textarea
    cols="30"
    rows="15"
    label="Text Body"
    value={textBody}
    onChange={e => this.handleChange(e)}
   />
   <input type="button" value="Add Tag" onClick={this.addTag} />
   <input type="button" value="Save" onClick={this.putProgress(title, textBody, tags)} />
   <h1>Tags</h1>
   <TagList tagListData={tags} />
   </div>
  );
  }
}
export default ViewEntry;
